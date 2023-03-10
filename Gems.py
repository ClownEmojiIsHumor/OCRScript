from PIL import ImageGrab, Image
import pytesseract
import pydirectinput
import pyautogui
import cv2
import time
import datetime
import traceback
import re
import keyboard
import win32gui
import numpy

WIN_TITLE = ".*LOST ARK.*"

initialTime = datetime.datetime.now()
#Add to path or change based on need


toggleBuyKeys = True
##############################################################################
targetGemLevel = 8
targetPrice = 1900
buyXthGem = 1

expectedSearchTime = 1200
whileThrottle = 500
##############################################################################
gemLevel = {
  9: (1090, 740), # lvl 9
  8: (990, 740), # lvl 8
  7: (890, 740), # lvl 7
}
# listings are 57 pixels apart
listingPosition = [
  (1520, 335), # 1st listing
  (1520, 392), # 2nd listing
  (1520, 449), # 3rd listing
  (1520, 506), # 4th listing
  (1520, 563), # 5th listing
  (1520, 620), # 6th listing
  (1520, 677), # 7th listing
  (1520, 734), # 8th listing
  (1520, 791), # 9th listing
  (1520, 848), # 10th listing
]
# fourDigitsX = 1548 # dont use this unless you really know what you're doing
# sixDigitsX = 1522
# sevenDigitsX = 1507
tenDigitsX = 1470
listingImagePosition = [
  (tenDigitsX, 325, 1599, 344), # 1st listing
  (tenDigitsX, 382, 1599, 401), # 2nd listing
  (tenDigitsX, 439, 1599, 458), # 3rd listing
  (tenDigitsX, 496, 1599, 515), # 4th listing
  (tenDigitsX, 553, 1599, 572), # 5th listing
  (tenDigitsX, 610, 1599, 629), # 6th listing
  (tenDigitsX, 667, 1599, 686), # 7th listing
  (tenDigitsX, 724, 1599, 743), # 8th listing
  (tenDigitsX, 781, 1599, 800), # 9th listing
  (tenDigitsX, 838, 1599, 857), # 10th listing
]

def toggleBuyKeys():
  global toggleBuyKeys
  toggleBuyKeys = not toggleBuyKeys

def autoBuy():
  keyboard.add_hotkey('ctrl+page up', toggleBuyKeys)
  # find_window_wildcard(WIN_TITLE)
  # debug
  # screenshot = ImageGrab.grab(bbox = (910, 461, 1004, 481)) # Bid/Buy
  # screenshot.save("Bid_Buy.png")
  # ocr = pytesseract.image_to_string(screenshot, config='--psm 6')
  # print(ocr.strip())
  # r, g, b = pyautogui.pixel(160, 118) # Mail icon red notification
  # print("rgb: ", r, g, b)
  # return

  click(1440, 925) # register
  press("esc")
  press("esc")

  lastBoughtTimestamp = None
  successfulPurchase = False
  iteration = 0
  sumPurchases = 0
  tooHighCount = 0
  errorCount = 0

  while(toggleBuyKeys):
    currentTime = datetime.datetime.now()
    
    if successfulPurchase == False or currentTime >= lastBoughtTimestamp + datetime.timedelta(seconds = 10 - whileThrottle / 1000 - expectedSearchTime / 1000):
      # pydirectinput.click()
      find_window_wildcard(WIN_TITLE)
      press("enter")
      # click(1185, 163) # close product window
      click(1520, 240) # search
      
      for _ in range(int(expectedSearchTime / 10)):
        r, g, b = pyautogui.pixel(1544, 923) # Bid/Buy
        if r == 110: # grey Bid/Buy
          # print ("successful search in {0}ms".format(i * 10))
          break
        sleep(10)
      
      if r == 233: # white Bid/Buy
        # print("retrying search")
        continue

      screenshot = ImageGrab.grab(bbox=listingImagePosition[buyXthGem]) # 10 digits
      screenshot = numpy.array(screenshot)
      thrshld = 40
      _, img_binarized = cv2.threshold(screenshot, thrshld, 255, cv2.THRESH_BINARY)
      screenshot = Image.fromarray(img_binarized)
      try:
        ocr = pytesseract.image_to_string(screenshot, lang='eng',config='--psm 6 -c tessedit_char_whitelist=0123456789')
        # imagePrice = int(ocr.strip().replace(".", ""))
        imagePrice = int(re.sub('[.,]', '', ocr.strip()))

        # if len(str(imagePrice)) < len(str(targetPrice)):
        #   print("{2} - len(ocr) < len(str(targetPrice)): str(imagePrice): {0}, str(targetPrice): {1}".format(str(imagePrice), str(targetPrice), currentTime))
        #   buyGem()
        if imagePrice <= targetPrice:
          # print("[{2}] imagePrice <= targetPrice: imagePrice: {0}, targetPrice: {1}".format(imagePrice, targetPrice, currentTime))
          lastBoughtTimestamp, successfulPurchase = buyGem()
          # print("[{0}] Bought: {1}".format(lastBoughtTimestamp, successfulPurchase))
          if successfulPurchase:
            print("[{0}] Successful buy for: {1}".format(lastBoughtTimestamp, imagePrice))

            if iteration % 10 == 0:
              fuseGem()

            sumPurchases += imagePrice
            iteration += 1
            averagePrice = sumPurchases / iteration
            averageTime = (lastBoughtTimestamp - initialTime) / iteration
            print("Successfully bought gems:", iteration)
            print("Average price:", averagePrice)
            print("Average time:", averageTime)
            print("tooHighCount:", tooHighCount)
        else:
          tooHighCount += 1
          print("imagePrice too high. ocr found: {0}tooHighCount: {1}".format(ocr, tooHighCount))
      except Exception:
        print(traceback.format_exc())
        screenshot.save("debug.png")
        errorCount += 1
        print("errorCount:", errorCount)
    sleep(whileThrottle)

def buyGem():
  click(listingPosition[buyXthGem][0], listingPosition[buyXthGem][1])
  click(1520, 925) # Bid/Buy

  for _ in range(int(expectedSearchTime / 10 - 70)):
    r, g, b = pyautogui.pixel(1103, 671) # Buy now
    if r == 224: # white 'buy now'
      # print ("successful product in {0}ms".format(i * 10))
      break
    sleep(10)
  if r != 224:
    # print("no product available")
    return None, False

  click(1120, 680) # Buy Now
  timestamp = datetime.datetime.now()
  
  sleep(200)
  screenshot = ImageGrab.grab(bbox = (910, 461, 1004, 481)) # Purchased
  ocr = pytesseract.image_to_string(screenshot, config='--psm 6')
  successfulPurchase = False
  if (ocr.strip() == "Purchased"):
    successfulPurchase = True
  click(955, 573) # Ok

  # Clear mail
  r, g, b = pyautogui.pixel(256, 94) # Mail slot #1
  if sum([r,g,b]) > 60: # checks for black pixel from mailbox
    click(370, 15) # Mail icon
  click(180, 110) # 1st mail
  sleep(200)
  click(570, 510) # Accept All
  click(650, 510) # Remove
  
  return timestamp, successfulPurchase

def fuseGem():
  press("i")
  sleep(100)
  click(1330, 820) # gem icon
  sleep(100)
  click(gemLevel[targetGemLevel][0], gemLevel[targetGemLevel][1])

  click(1090, 800) # fuse
  click(920, 585) # yes

  sleep(1500) # wait for fuse animation
  click(1665, 220) # close inventory window

def click(x, y, button="left"):
  pydirectinput.click(x=x, y=y, button=button)

# sleep in ms
def sleep(seconds):
  time.sleep(seconds / 1000)

def press(key):
  pydirectinput.press(key)

def _window_enum_callback(hwnd, wildcard):
  """Pass to win32gui.EnumWindows() to check all the opened windows"""
  if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
    win32gui.SetForegroundWindow(hwnd)

def find_window_wildcard(wildcard):
  """find a window whose title matches the wildcard regex"""
  win32gui.EnumWindows(_window_enum_callback, wildcard)

autoBuy()