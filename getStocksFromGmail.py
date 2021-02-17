import pickle
import os.path
import email
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
from usefulFunctions import split_text

pd.set_option("display.max_rows", None, "display.max_columns", None)
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def getAllInfo(EXTRA_SEARCH_ARGS):
    #connect to the gmail account
    service = getService()
    #get the portfolio info
    dfMail = getMyPortfolio(service, EXTRA_SEARCH_ARGS)
    return pd.DataFrame(dfMail)

def getMyPortfolio(service, EXTRA_SEARCH_ARGS):
    #get the portofolio info
    dfMail = getMyPortofolio(service, EXTRA_SEARCH_ARGS)
    return pd.DataFrame(dfMail)

def getMyPortofolio(service, EXTRA_SEARCH_ARGS):
    #search for label
    searchString = "from:(@trading212.com) subject:(Contract Note Statement from Trading 212)" + EXTRA_SEARCH_ARGS
    #get the id list of the emails that match as well as their number
    list_of_matching_ids, numberResults = search_messages(service, 'me', searchString)
    #print the total matching emails for the user
    print("Number of investing emails: " + str(numberResults) + "\n")    
            
    gmailStockData = [["Date", "Time", "Id", "Ticker", "ISIN", "Order Type", 
                       "Direction", "Quantity","Total" ,"Commission", "Charges and Fees"]]

    #Take each email (only applicable if there is at least one email)
    if numberResults > 0:
        #loop for each email
        for i in range (numberResults):
            get_message(service, 'me', list_of_matching_ids[i], gmailStockData)
        #return the data
        return pd.DataFrame(data = gmailStockData[1:][0:],       # values
                            columns = gmailStockData[0][0:])     # 1st row as the column names
    return pd.DataFrame()

def getService():    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service



def search_messages(service, user_id, searchString):
    try:
        search_id = service.users().messages().list(userId=user_id, q=searchString).execute()

        #find the number of results that match
        numberResults = search_id['resultSizeEstimate']

        #get the ids of the result
        if numberResults > 0:
            #create a list to put all the ids
            final_list = []

            #get all the ids
            message_ids = search_id['messages']
            
            for ids in message_ids:                
                #add each id in the list
                final_list.append(ids["id"])
                
            #return the list
            return final_list, numberResults
        else:            
            print("There were no results for that search. Returning an empty string")
            #if there are no messages return an empty string
            return "", numberResults
    
    except Exception as error:
        print('An error occurred in the search_messages function: %s' % error)



def get_message(service, user_id, msg_id, gmailStockData):
    try:
        #get the message in raw format
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        
        #encode the message in ASCII format
        msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
        #put it in an email object
        mime_msg = email.message_from_string(msg_str)
        #get the date and time of the email
        date = mime_msg['date']
        
        
        #get the plain and html text from the payload
        for part in mime_msg.walk():
            
        #each part is a either non-multipart, or another multipart message
        #that contains further parts... Message is organized like a tree
            if part.get_content_type() == 'text/plain':
                #prints the raw text that we want
                text = part.get_payload()              
                get_formatted_text(text, gmailStockData)
    
    except Exception as error:
        print('An error occurred in the get_message function: %s' % error)



def get_formatted_text(text, gmailStockData):
    #find number of positions in email
    posNum = text.count("POS")

    for i in range(posNum):

        orderId = split_text(text, "POS", " ")
        orderId = "POS" + orderId        
        ticker = split_text(text, str(orderId), "/")        
        isin = split_text(text, str(ticker+'/'), " ")

        #take the line and check if you can find the word Buy
        direction = split_text(text, str(orderId), "POS")
        direction = direction.strip()
        if direction.find("Buy")!=-1:
            direction = "Buy"
        else:
            direction = "Sell"
        
        #get all the useful info between the direction and the commision
        #basically quantity, pricePerUnit, total, date, time
        usefulInfo = split_text(text, str(direction), "")
        #put those info in their respective variables
        quantity, pricePerUnit, total, date, time, commission, chargesAndFees, orderType = usefulInfo.split('\n', 7)

        #clean the variables from the word EUR
        pricePerUnit = pricePerUnit.split("EUR")[0]
        total = total.split("EUR")[0]

        #remove all spaces
        quantity = quantity.strip()        
        pricePerUnit = pricePerUnit.strip()        
        total = total.strip()
        date = date.strip()
        time = time.strip()
        commission = split_text(commission, "", "EUR")
        chargesAndFees = split_text(chargesAndFees, "", "EUR")
        orderType = split_text(orderType, "", "\r")

        #convert all numbers to float
        quantity = float(quantity)
        total = float(total)

        #if commission or chargesAndFees == 0 make them NaN
        #in order to be the same with the orders csv
        if commission == "0":
            commission = float("nan")
        else:
            commission = float(commission)

        if chargesAndFees == "0":
            chargesAndFees = float("nan")
        else:
            chargesAndFees = float(chargesAndFees)

        #append everything to the array
        gmailStockData.append([date, time, orderId, ticker, isin, orderType, direction, quantity, total, commission, chargesAndFees])
        
        #cut the string in each loop
        if(i != posNum - 1):
            text = text.split("POS", 1)[1]
            text = "POS" + text.split("POS", 1)[1]

