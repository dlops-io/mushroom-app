import sys
import os
import requests
import time
import shutil
from selenium import webdriver
import threading
from queue import Queue


dataset_path = "/persistent/dataset"
thread_count = 50
threads = []
# Initial queue
queue = Queue(0)


class Downloader(threading.Thread):
    def __init__(self, queue, thread):
        threading.Thread.__init__(self)
        self.queue = queue
        self.thread = thread

    def run(self):
        while self.queue.empty() == False:
            item = self.queue.get()

            # print("Thread:",self.thread,item)
            # time.sleep(3)
            download_from_url(item["url"], item["img_dir"], item["file_path"])

            self.queue.task_done()


def download_from_url(url, img_dir, file_path):
    """Downloading the actual image from Google

    INPUTS
    =======
    url: unifrom resource locator; the address of a given unique resource on the Web, in this case an image of a pair of Jordans
    img_dir: Not accessed
    file_path:  where to save the Jordans image

    """
    try:
        img_path = os.path.basename(url)
        #file_path = os.path.join(img_dir, img_path)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        print("Error in url:", url)
        print(e)


def download_google_images(num_images_requested, search_term_list):
    print("download_google_images...")
    start_time = time.time()

    # Setup dataset folder
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
    os.mkdir(dataset_path)

    # Each scrolls provides 400 image approximately
    number_of_scrolls = int(num_images_requested / 400) + 1

    # Firefox Options
    # set up a webdriver for Firefox
    options = webdriver.FirefoxOptions()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    images_link = None
    for search_term in search_term_list:
        print("Searching for :", search_term)
        browse_link = 'https://www.google.com/search?q=' + search_term
        print("link:", browse_link)
        browser.get(browse_link)

        # Go to Google Images
        # we search Google by using the CSS selector (like regex for HTML)
        # we find an element ‘a’ that contains the class with “hide-focus-ring”; this will give us the Google images
        # migrate through each of the links b/c there’s one for shopping, news, books, etc., and find the one that shows it to be =isch&; this will identify it as Google Images

        # images_links = browser.find_elements_by_xpath(
        #     '//a[contains(@class, "hide-focus-ring")]')
        images_links = browser.find_elements_by_xpath(
            '//a[contains(@data-hveid, "CAEQAw")]')
        for link in images_links:
            # print(link)
            # on the element we get the href
            link_href = link.get_attribute("href")
            print(link_href)

            # Find images link
            if "&tbm=isch" in link_href:
                images_link = link
                break

        if images_link is None:
            raise ValueError('Google Images link was not found')

        # Wait to make sure that Google knows this is not automated
        time.sleep(5)

        # Go to images
        #images_link = images_links[0]
        print("Going to link:", images_link.get_attribute("href"))
        # Seleniuam was originally a front-end testing tool where we write out test scenarios for 50 cases, such as a user clicking on certain things; Facebook and Instagram use Selenium for fake likes and fake comments
        # since Selenium can do anything that a human is doing, we can click on the "Images" link for Google
        images_link.click()

        # Scroll to get more images
        # we want to keep on scrolling and clicking the "show more results" button so that we can capture as many thumbnails as possible to get as many Jordan shoe images as possible
        print("number_of_scrolls:", number_of_scrolls)
        for _ in range(number_of_scrolls):
            for __ in range(10):
                # multiple scrolls needed to show all 400 images
                browser.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)
            # to load next 400 images
            # we've scrolled to the bottom of this page, so now we'd like to show more results again
            time.sleep(5)
            # try to find show more results bottom
            try:
                # if found click to load more image
                browser.find_element_by_xpath(
                    "//input[@value='Show more results']").click()
            except Exception as e:
                print(e)
                # if not exit
                print("End of page")
                break

        # Image link store
        # we’re at first collecting the urls in a set, and then actually saving images
        # we're using a set because soemtimes there are duplicate urls
        imgs_urls = set()
        # Find the thumbnail images
        # -find all “a” elements to get the image, and that will allow us to get the direct link to the image
        thumbnails = browser.find_elements_by_xpath(
            '//a[@class="wXeWr islib nfEiy"]')
        print("Number of thumbnails:", len(thumbnails))
        # loop over the thumbs to retrive the links
        for thumbnail in thumbnails:
            # check if reached the request number of links
            if len(imgs_urls) >= num_images_requested:
                break
            try:
                thumbnail.click()
                time.sleep(2)
            except Exception as error:
                print("Error clicking one thumbnail : ", error)
            # Find the image url
            url_elements = browser.find_elements_by_xpath(
                '//img[@class="n3VNCb"]')
            # check for the correct url
            for url_element in url_elements:
                try:
                    url = url_element.get_attribute('src')
                except e:
                    print("Error getting url")
                if url.startswith('http') and not url.startswith('https://encrypted-tbn0.gstatic.com'):
                    #print("Found image url:", url)
                    imgs_urls.add(url)

        print('Number of image urls found:', len(imgs_urls))

        # Wait 5 seconds
        time.sleep(5)

        # Save the images
        # creating the path for where to save the images
        img_dir = os.path.join(
            dataset_path, search_term.lower().replace(" ", "_"))
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        count = 0
        if len(imgs_urls) > 0:
            for url in imgs_urls:
                file_path = os.path.join(img_dir, '{0}.jpg'.format(count))
                count += 1
                queue.put({"url": url, "img_dir": img_dir,
                          "file_path": file_path})

            # Execute downloads from queue in a thread
            # a Queue here makes it faster
            # put all the links in a queue, and then performing the downloads in parallel using the threading library (e.g. we have 50 threads, and can download them all at once)
            for i in range(thread_count):
                thread = Downloader(queue, i)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    # Quit the browser
    browser.quit()

    execution_time = (time.time() - start_time) / 60.0
    print("Download execution time (mins)", execution_time)
