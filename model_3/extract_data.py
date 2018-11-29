from time import sleep

import click
from selenium import webdriver


@click.command("load_data")
def load_data_command():
    load_data()


def load_data():
    # Set up browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("no-sandbox")
    chrome_options.add_argument("headless")
    chrome_options.add_argument("--window-size=1280,960")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en_CA'})
    driver = webdriver.Chrome(options=chrome_options)

    # GET page
    driver.get("https://3.tesla.com/en_CA/model3/design?redirect=no")

    # Extract standard battery data
    standard_battery_availability = driver.find_element_by_class_name("group--disclaimer").text

    # Extract trim data
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

    # Show trim and standard battery details
    print(f"Mid Range, RWD: {mr_rwd_full_price} | {mr_rwd_avail}")
    print(f"Long Range, AWD: {lr_awd_full_price} | {lr_awd_avail}")
    print(f"Long Range, Performance: {lr_perf_full_price} | {lr_perf_avail}")
    print(f"{standard_battery_availability}")

    # Reset trim selection
    mr_rwd.click()

    # Navigate to exterior options
    nav_headers = driver.find_elements_by_class_name("packages-options--nav-title")
    nav_headers[1].click()
    sleep(1)

    # Get exterior options list
    exterior_options = driver.find_elements_by_class_name("group--options_asset--container")

    # Split paints and wheels
    paint_options, wheel_options = exterior_options[:5], exterior_options[5:]

    # Extract paint data
    paints = {}
    for paint_opt in paint_options:
        paint_opt.click()
        paint_name = driver.find_elements_by_class_name("group-option--detail-container_name")[0].text
        paint_price = driver.find_elements_by_class_name("group-option--detail-container_price")[0].text
        paints[paint_name] = paint_price
    paint_options[0].click()

    # Extract wheel data
    wheels = {}
    for wheel_opt in wheel_options:
        wheel_opt.click()
        wheel_name = driver.find_elements_by_class_name("group-option--detail-container_name")[1].text
        wheel_price = driver.find_elements_by_class_name("group-option--detail-container_price")[1].text
        wheels[wheel_name] = wheel_price
    wheel_options[0].click()

    # Display paint and wheel data
    for paint_name, paint_price in paints.items():
        print(f"Paint {paint_name}: {paint_price}")

    for wheel_name, wheel_price in wheels.items():
        print(f"Wheels {wheel_name}: {wheel_price}")

    # Navigate to Interior options
    nav_headers[2].click()
    sleep(1)

    interior_options = driver.find_elements_by_class_name("group--options_asset--container")

    # Extract interior options
    interiors = {}
    for interior in interior_options:
        interior.click()
        interior_name = driver.find_element_by_class_name("group-option--detail-container_name").text
        interior_price = driver.find_element_by_class_name("group-option--detail-container_price").text
        interiors[interior_name] = interior_price
    interior_options[0].click()

    # Display interior options
    for interior_name, interior_price in interiors.items():
        print(f"Interior {interior_name}: {interior_price}")

    # Navigate to Autopilot
    nav_headers[3].click()
    sleep(1)

    # Extract EAP details
    eap_price = driver.find_element_by_class_name("group--options_card-container_price").text
    eap_later_price = driver.find_element_by_class_name("group--option-disclaimer").text

    print(f"EAP: {eap_price}, {eap_later_price}")

    # Navigate to Payment
    nav_headers[4].click()
    sleep(1)

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
        }
    }

    print(data)

    return data


if __name__ == '__main__':
    load_data()
