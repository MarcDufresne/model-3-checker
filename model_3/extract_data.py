import datetime
import os
from time import sleep

import click
import ujson
from selenium import webdriver

from model_3 import action, done


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

    previous_change = previous_data.get("last_changed", None)
    previous_data.pop("last_updated", None)
    previous_data.pop("last_changed", None)

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

    # GET page
    driver.get("https://3.tesla.com/en_CA/model3/design?redirect=no")

    # Extract standard battery data
    action("Getting standard battery availability... ")
    standard_battery_availability = driver.find_element_by_class_name("group--disclaimer").text
    done()

    # Extract trim data
    action("Getting trims... ")
    trim_options = driver.find_elements_by_class_name("group--options_block")
    mr_rwd = trim_options[0]
    lr_awd = trim_options[1]
    lr_perf = trim_options[2]

    mr_rwd.click()
    finance_item_prices = driver.find_elements_by_class_name("finance-item--price")
    mr_rwd_full_price = finance_item_prices[1].text
    mr_rwd_avail = driver.find_element_by_class_name("delivery-timing--date").text

    lr_awd.click()
    finance_item_prices = driver.find_elements_by_class_name("finance-item--price")
    lr_awd_full_price = finance_item_prices[1].text
    lr_awd_avail = driver.find_element_by_class_name("delivery-timing--date").text

    lr_perf.click()
    finance_item_prices = driver.find_elements_by_class_name("finance-item--price")
    lr_perf_full_price = finance_item_prices[1].text
    lr_perf_avail = driver.find_element_by_class_name("delivery-timing--date").text

    # Reset trim selection
    mr_rwd.click()
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
    driver.find_element_by_class_name("finance-content--modal").click()
    driver.find_element_by_class_name("tds-tabs--vertical").find_elements_by_class_name("tds-tab-label")[2].click()
    sleep(1)

    try:
        regions_list = driver.find_element_by_class_name("incentives--region-list")
    except Exception:
        driver.find_element_by_class_name("action-trigger--link").click()
        regions_list = driver.find_element_by_class_name("incentives--region-list")

    regions_links = regions_list.find_elements_by_class_name("action-trigger--link")

    incentives = {}

    region_index = 0
    while region_index < len(regions_links):
        region = (driver.find_element_by_class_name("incentives--region-list")
                  .find_elements_by_class_name("action-trigger--link")[region_index])
        region_name = region.text
        region.click()
        incentive_block = driver.find_element_by_class_name("incentives--value-block")
        incentive_value = incentive_block.find_element_by_class_name("value").text
        incentives[region_name] = incentive_value
        driver.find_element_by_class_name("action-trigger--link").click()
        region_index += 1
    done()

    data = {
        "trims": {
            "mr_rwd": {
                "price": mr_rwd_full_price,
                "availability": mr_rwd_avail
            },
            "lr_awd": {
                "price": lr_awd_full_price,
                "availability": lr_awd_avail
            },
            "lr_perf": {
                "price": lr_perf_full_price,
                "availability": lr_perf_avail
            }
        },
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
    now_isoformat = datetime.datetime.utcnow().isoformat(sep=" ")

    if changed:
        last_changed = now_isoformat

    data["last_updated"] = now_isoformat
    data["last_changed"] = last_changed or now_isoformat

    click.secho(f"\nData:", fg="blue")
    click.echo(ujson.dumps(data, indent=2))

    action("\nWriting 'data.json' file... ")
    with open(data_json_filepath, mode="w") as f:
        f.write(ujson.dumps(data))
    done()

    return data


if __name__ == '__main__':
    load_data_command()
