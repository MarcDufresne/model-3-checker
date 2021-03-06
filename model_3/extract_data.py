import os
from time import sleep

import arrow
import click
import ujson
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from model_3 import action, done


UNKNOWN_AVAILABILITY_TEXT = "Unknown Availability"


@click.command("load_data")
@click.option("--display", is_flag=True)
def load_data_command(display: bool):
    load_data(headless=not display)


def load_data(headless: bool = True):

    action("Loading previous data... ")
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data_json_filepath = os.path.join(cur_dir, os.path.pardir, 'docs', 'data.json')
    with open(data_json_filepath, mode="r") as data_file:
        previous_data = ujson.loads(data_file.read())
    done()

    # Set up browser
    action("Starting Chrome browser... ")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("no-sandbox")
    if headless:
        chrome_options.add_argument("headless")
    chrome_options.add_argument("--window-size=1280,960")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en_CA'})
    driver = webdriver.Chrome(options=chrome_options)
    done()

    regions = [
        "en_CA",
        "en_US",
    ]
    data = {}

    for region in regions:
        previous_region_data = previous_data.get(region, {})
        previous_change = previous_region_data.get("last_changed", None)
        previous_region_data.pop("last_updated", None)
        previous_region_data.pop("last_changed", None)

        # GET page
        driver.get(f"https://3.tesla.com/{region}/model3/design?redirect=no")

        # Extract standard battery data
        action("Getting standard battery availability... ")
        standard_battery_availability = driver.find_element_by_class_name("group--disclaimer").text
        done()

        # Extract trim data
        action("Getting trims... ")

        main_trim_container = driver.find_element_by_class_name("group--child-container")
        trim_containers = main_trim_container.find_elements_by_class_name("child-group--container")

        first_trim_option = None
        trims = {}

        for trim_container in trim_containers:
            trim_name = trim_container.find_element_by_class_name("text-loader--section-title").text
            trim_options_containers = trim_container.find_elements_by_class_name("group--options_block--name")
            trim_options = []
            for trim_options_container in trim_options_containers:
                if not first_trim_option:
                    first_trim_option = trim_options_container

                trim_options_container.click()
                trim_option_name = trim_options_container.text
                trim_option_price = driver.find_elements_by_class_name("finance-item--price")[1].text
                try:
                    trim_option_avail = driver.find_element_by_class_name("delivery-timing--date").text
                except NoSuchElementException:
                    trim_option_avail = UNKNOWN_AVAILABILITY_TEXT
                trim_options.append({
                    "name": trim_option_name,
                    "price": trim_option_price,
                    "availability": trim_option_avail
                })
            trims[trim_name] = trim_options

        first_trim_option.click()
        done()

        # Navigate to exterior options
        nav_headers = driver.find_elements_by_class_name("packages-options--nav-title")
        nav_headers[1].click()
        sleep(1)

        # Get exterior options list
        exterior_options = driver.find_elements_by_class_name("group--options_asset--container")

        # Split paints and wheels
        paint_options, wheel_options = exterior_options[:5], exterior_options[5:]

        # Extract paint data
        action("Getting paint options... ")
        paints = {}
        for paint_opt in paint_options:
            paint_opt.click()
            paint_name = driver.find_elements_by_class_name("group-option--detail-container_name")[0].text
            paint_price = driver.find_elements_by_class_name("group-option--detail-container_price")[0].text
            paints[paint_name] = paint_price
        paint_options[0].click()
        done()

        # Extract wheel data
        action("Getting wheel options... ")
        wheels = {}
        for wheel_opt in wheel_options:
            wheel_opt.click()
            wheel_name = driver.find_elements_by_class_name("group-option--detail-container_name")[1].text
            wheel_price = driver.find_elements_by_class_name("group-option--detail-container_price")[1].text
            wheels[wheel_name] = wheel_price
        wheel_options[0].click()
        done()

        # Navigate to Interior options
        nav_headers[2].click()
        sleep(1)

        interior_options = driver.find_elements_by_class_name("group--options_asset--container")

        # Extract interior options
        action("Getting interior options... ")
        interiors = {}
        for interior in interior_options:
            interior.click()
            interior_name = driver.find_element_by_class_name("group-option--detail-container_name").text
            interior_price = driver.find_element_by_class_name("group-option--detail-container_price").text
            interiors[interior_name] = interior_price
        interior_options[0].click()
        done()

        # Navigate to Autopilot
        nav_headers[3].click()
        sleep(1)

        # Extract EAP details
        action("Getting EAP pricing... ")
        eap_price = driver.find_element_by_class_name("group--options_card-container_price").text
        eap_later_price = driver.find_element_by_class_name("group--option-disclaimer").text
        done()

        # Navigate to Payment
        nav_headers[4].click()
        sleep(1)

        # Incentives
        action("Getting incentives... ")
        incentives = get_incentives(driver)
        done()

        region_data = {
            "trims": trims,
            "std_battery": standard_battery_availability,
            "paint": paints,
            "wheels": wheels,
            "interiors": interiors,
            "eap": {
                "price": eap_price,
                "later": eap_later_price
            },
            "incentives": incentives,
        }

        changed = previous_data != data

        last_changed = previous_change
        now_format = arrow.utcnow().format(fmt="MMM D YYYY, HH:mm", locale='en_ca')

        if changed:
            last_changed = now_format

        region_data["last_updated"] = now_format
        region_data["last_changed"] = last_changed or now_format

        click.secho(f"\nData for {region}:", fg="blue")
        click.echo(ujson.dumps(region_data, indent=2))

        data[region] = region_data

    action("\nWriting 'data.json' file... ")
    with open(data_json_filepath, mode="w") as f:
        f.write(ujson.dumps(data))
    done()

    return data


def get_incentives(driver):
    driver.find_element_by_class_name("finance-content--modal").click()
    driver.find_element_by_class_name("tds-tabs--vertical").find_elements_by_class_name("tds-tab-label")[2].click()
    sleep(1)

    try:
        try:
            driver.find_element_by_class_name("incentives--region-list")
        except NoSuchElementException:
            driver.find_element_by_class_name("action-trigger--link").click()
        finally:
            regions_list = driver.find_element_by_class_name("incentives--region-list")
            incentives = _get_list_incentives(driver, regions_list)
    except NoSuchElementException:
        incentives = _get_dropdown_incentives(driver)

    return incentives


def _get_list_incentives(driver, regions_list):
    regions_links = regions_list.find_elements_by_class_name("action-trigger--link")

    incentives = {}

    try:
        federal_incentive_block = driver.find_element_by_class_name("incentives--federal")
        incentives["Federal"] = federal_incentive_block.find_element_by_class_name("value").text
    except NoSuchElementException:
        pass

    region_index = 0
    while region_index < len(regions_links):
        inc_region = (driver.find_element_by_class_name("incentives--region-list")
                      .find_elements_by_class_name("action-trigger--link")[region_index])

        region_name = inc_region.text

        inc_region.click()

        incentive_block = driver.find_element_by_class_name("incentives--value-block")
        incentive_value = incentive_block.find_elements_by_class_name("value")[-1].text
        incentives[region_name] = incentive_value

        driver.find_element_by_class_name("action-trigger--link").click()
        region_index += 1
    return incentives


def _get_dropdown_incentives(driver):
    incentives_container = driver.find_element_by_class_name("financial--highlighted-summary")

    try:
        # Try to reset incentive
        incentives_container.find_element_by_class_name("action-trigger--link").click()
    except NoSuchElementException:
        pass

    incentives = {}

    regions_dropdown = Select(incentives_container.find_element_by_class_name("tds-input-select"))
    for index, option in enumerate(regions_dropdown.options):
        regions_dropdown.select_by_index(index)
        list_items = incentives_container.find_elements_by_class_name("line-item")[1:]
        for item in list_items:
            try:
                label_container = item.find_element_by_class_name("line-item--label")
                label = label_container.text
                try:
                    link_text = label_container.find_element_by_class_name("action-trigger--link").text
                    label = label[:-len(link_text)]
                except NoSuchElementException:
                    pass
                amount = item.find_element_by_class_name("line-item--value").text
                incentives[label] = amount
            except NoSuchElementException:
                pass

        # Reset
        incentives_container.find_element_by_class_name("action-trigger--link").click()
        regions_dropdown = Select(incentives_container.find_element_by_class_name("tds-input-select"))

    return incentives


if __name__ == '__main__':
    load_data_command()
