import socket
import MySQLdb
import time
import sys
import atexit

start_program_time = time.time()
host = ''
port = 5560
storedValue = "Hey There, What's up?"
reply1 = " "
num_client = 0



def setupServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Created.")
    try: 
        s.bind((host, port))
        print("Socket Bind Complete.")
        return s
    except Exception as e:
        print(e)
        if e.errno == 10048:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((socket.gethostname(),port))
                print("Socket Bind Complete.")
                return s
            except Exception as e:
                print(e)
                print("We are Facing Problem. Try Again.")
                sys.exit()

    
print("Clients Connected %i" %num_client)
def setupConnection():
    s.listen(1) # Allows one connection at a time.
    print("###....Waiting for the Client to connect. ....##")
    conn, address = s.accept()
    print("We are connected to :" + address[0] + ":" + str(address[1]))
    print("Clients Connected %i" %(num_client + 1))
    return conn

def GET():
    print("Received Command : GET")
    reply = storedValue
    
    host="<confidential>"
    user="<confidential>"
    passwd="<confidential>"
    db="<confidential>"
    
    

    #Connecting to database
    print("\nGot the Credentials")
    try:
        print("Connecting to the Database")
        db = MySQLdb.connect(host, user, passwd, db, connect_timeout = 2)
        print("##....Connected to the Database....##")
        cur = db.cursor()
        sql_query = "UPDATE CONSUMER SET NAME = 'Rahul' WHERE AADHAAR_NUMBER = '1'"
        try:
            print("##....Executing the commit....##")
            cur.execute(sql_query)
            print("##....Commiting the Query....##\n")
            db.commit()
            reply = "Query Executed Succesfully"
        except:
            print("##....Error Executing the Command....##\n")
            db.rollback()
        db.close()
    except:
        print("We got some Error Connecting to database. Please Try again\n")
        reply = "We got some Error Connecting to database. Please Try again"
    return reply

def SEND(dataMessage):
    print("Received Command : SEND")
    dataMessage = dataMessage.split(" ")

    print(dataMessage)
    CONSUMER_ID = str(dataMessage[0])
    read_date = str(dataMessage[1])
    read_time = str(dataMessage[2])
    current_weight = str(dataMessage[3])
    use_weight = str(dataMessage[4])
    weight_used = str(dataMessage[5])
    weight_at_recharge_status = 0
    #print("CONSUMER_ID :" + str(CONSUMER_ID) +  "\tDate :" + str(read_date) + "\tTime :" + str(read_time) + "\tWeight : " + str(weight))

    host="sql143.main-hosting.eu"
    user="u402156879_lpg1"
    passwd="!prajjwala2k18"
    db="u402156879_lpg1"

    #Connecting to database
    print("\nGot the Credentials")
    try:
        print("Connecting to the Database")
        db = MySQLdb.connect(host, user, passwd, db, connect_timeout = 2, )
        print("##....Connected to the Database....##")
        cur = db.cursor()
        sql_query = "INSERT INTO `CONSUMER_REALTIME_GAS_USAGE`(`CONSUMER_ID`,`DATE`,`TIME`,`GAS_LEFT`) VALUES('%s','%s','%s','%s')" %(CONSUMER_ID, read_date, read_time, current_weight)
        try:
            print("##....Executing the commit....##")
            cur.execute(sql_query)
            print("##....Commiting the Query....##\n")
            db.commit()
            print("####.....Query Executed Succesfully....####")
        except Exception as e:
            print(e)
            reply = "Error1 " + str(e) + "##....Error Executing the Command....##\n"
            db.rollback()
        reply = str(use_weight) + " " + str(weight_at_recharge_status)
            
        if(use_weight == 0 and weight_used <= 0):
                sql_query1 = "SELECT * FROM CONSUMER_GAS_USAGE WHERE CONSUMER_ID = '%i' AND STATUS = '%i'" %(CONSUMER_ID, 1)
                try:
                    cur.execute(sql_query1)
                    results = cur.fetchall()
                    for row in results:
                        print("##....Query Executed....##")
                        print("##....Fetching Data....##")
                        RECHARGE_DATE = row[2]
                        RECHARGE_TIME = row[3]
                        RECHARGE_AMOUNT = row[4]
                        RECHARGE_GAS_EQUIVALENT = row[5]
                        
                        use_weight = RECHARGE_GAS_EQUIVALENT
                        # Now print fetched result
                        print("RECHARGE_DATE='%s'\nRECHARGE_TIME='%s'\nRECHARGE_AMOUNT='%s'\nRECHARGE_GAS_EQUIVALENT='%s'" %(RECHARGE_DATE,RECHARGE_TIME,RECHARGE_AMOUNT,RECHARGE_GAS_EQUIVALENT))

                        update_query = "UPDATE CONSUMER_GAS_USAGE SET STATUS = '%i' WHERE CONSUMER_ID = '%s' AND RECHARGE_TIME = '%s'" %(0,CONSUMER_ID, RECHARGE_TIME)
                        print(update_query)
                        cur.execute(update_query)
                        db.commit()
                        print("\n##....Status Updated....##\n")

                        if(use_weight > 0):
                            weight_at_recharge_status = 1
                            print("\nSystem Recharged for Rs. " + str(use_weight) + "\n")
                            reply = str(use_weight) + " " + str(weight_at_recharge_status)
                        break;
                except Exception as e:
                        print(e)
                        reply = "Error1 " + str(e) + "##....Error Executing the Command....##\n"
                        db.rollback()

        db.close()
    except Exception as e:
        print(e)
        reply = "Error1 " + str(e) + "We got some Error Connecting to database. Please Try again"

    return reply


def dataTransfer(conn):     # A big loop that sends/Receive data until not told to.  
    reply1 = " "
    while True:
        try:
            data = conn.recv(1024)
            data = data.decode('utf-8')
            start_dataTransfer_time = time.time()
        except Exception as e:
            print(e)
            print(str(e.errno))
            if e.errno == 10053 or e.errno == 10054:        # Error: An established connection was aborted by the software in your host machine
                while True:
                    try:
                        conn = setupConnection()
                        dataTransfer(conn)
                        break
                    except Exception as e:
                        print(e)
                        conn = setupConnection()
                        dataTransfer(conn)
                        break
        #spit data such that you separeate the command from the rest of the data

        dataMessage = data.split(' ', 1)
        command = dataMessage[0]
        print(dataMessage)
        if command == "GET":
            reply = GET()
        elif command == "SEND" and len(dataMessage) > 1 and dataMessage[1] != '':
            try:
                reply = SEND(dataMessage[1])        #Sends the Strings received excluding SEND ccommand
            except Exception as e:
                print(e)
                reply = "Error1 " + str(e) + ". Error. Try again."
        elif command == "KILL":
            print("Our Client has left us.")
            break
        elif command == " ":
            break
        else:
            reply = "Unknown Command"
        del command

        if(time.time() - start_dataTransfer_time) < 10:
            try:
                #send the reply back to the  Client
                conn.sendall(str.encode(str(reply)))
                print("Data has been sent")
            except Exception as e:
                print(e)
        else:
            print("Unable to send Data")
            reply1 = reply1 + reply
    conn.close()



s = setupServer()
while True:
    try:
        conn = setupConnection()
        dataTransfer(conn)
        
        
    except:
        conn = setupConnection()
        dataTransfer(conn)


def exitfunc():
    print("Ok. Bye")
    time.sleep(1)
    s.close()
atexit.register(exitfunc)

