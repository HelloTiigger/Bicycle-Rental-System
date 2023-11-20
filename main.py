import os
import csv
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
import numpy as np
import json
from json import JSONEncoder
from datetime import timedelta

#integer helper function:
def get_Integer(prompt, min_val=None, max_val=None):
    while True:
        try:
            r = int(input(prompt))
            if (min_val is None or r >=min_val) and (max_val is None or r <=max_val):
                return r
            else:
               raise ValueError 
        except ValueError:
            print(f"Invalid Entry! Please enter an integer value{' between ' + str(min_val) + ' and ' + str(max_val) if min_val is not None and max_val is not None else ''}.")

class StockEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
        
#simulate time:
class SimulatedTime:
    def __init__(self, initial_time=None):
        if initial_time:
            self.current_time = initial_time
        else:
            self.current_time = datetime.datetime.now()

    def set_time(self, new_time):
        self.current_time = new_time

    def advance_time(self, hours=0, minutes=0):
        self.current_time += datetime.timedelta(hours=hours, minutes=minutes)
        self.initial_time = self.current_time

    def get_current_time(self):
        return self.current_time

#price list
PRICING = {
    'Adult_single': {'rate':8,'time_frame':60},
    'Kids': {'rate':6,'time_frame':60},
    'Tandem':{'rate':16,'time_frame':60},
    'Family': {'rate':35,'time_frame':60},
    'Pedal_go_karts':{'rate':35,'time_frame':30}
    }

#bicycle class
class MyBicycle():
    order_counter = 0
    
    def __init__(self, b):
        self.Type = b
        self.adding = 0
        self.renting = 0
        self.rentID = ''
        self.rate = PRICING[b]['rate']
        self.time_frame = PRICING[b]['time_frame']
        self.effective_hours = 0
        
    def nowkeep(self):
        return self.adding - self.renting
        
    def add(self, qty):
        self.adding += qty
    
    def rent(self):
        MyBicycle.order_counter += 1
        self.rentID = "order-" + str(MyBicycle.order_counter)
        self.renting += 1
        return self.rentID
    
    def returnit(self):
        self.renting -= 1
     
    def calculate_first_fee(self,b, h):
        h = float(h)
        
        #Calculate the effective booking hours
        current_day = simulated_time.get_current_time().weekday()
        self.effective_hours = h
        if 0 <= current_day <= 4 and h > 2: #0 is Sunday
            self.effective_hours = h - 1.0 
        elif (current_day == 5 or current_day == 6) and h > 3:
            self.effective_hours = h - 1.0
            
        #Calculate the fee
        fee = self.effective_hours * self.rate * (60 / self.time_frame)
        return fee     

#sub-class
class Transaction():
    def __init__(self, ID, h=0):
        self.rentID = ID
        self.start_time = simulated_time.get_current_time()
        self.end_time = simulated_time.get_current_time()
        self.using_time = 0
        self.booked_time = h
        self.over = 0
        
    def start_tracking(self):
        self.start_time = simulated_time.get_current_time()
        
    def end_tracking(self):
        self.end_time = simulated_time.get_current_time()
        self.using_time = self.end_time - self.start_time
        return self.using_time
    
    def calculate_fee(self):
        booked_minutes = self.booked_time * 60
        used_minutes = self.using_time.total_seconds() / 60
        if used_minutes <= booked_minutes:
            return self.calculate_fee(self.booked_time)
        else:
            extra_minutes = used_minutes - booked_minutes
            return self.calculate_fee(self.booked_time) + MyBicycle.rate * (extra_minutes / MyBicycle.time_frame)

#BicycleKeeper
class Controller():
    
    bicycles = {}
    transactions = {}
    completed_orders = {}
    fee={}
    
    def add_new_product(self, b, qty):
        if b in self.bicycles:
            self.bicycles[b].add(qty)
        else:
            self.bicycles[b] = MyBicycle(b)
            self.bicycles[b].add(qty)
        
    def update_Inventory(self):
        with open("bikes.json", "w") as write_file:
            json.dump([self.bicycles], write_file, cls=StockEncoder, indent=4)

        with open("bikes.json", "r") as read_file:
            s = json.load(read_file)
        return 'Inventory json file is prepared!'
    
    def display_Inventory(self):
        return self.bicycles
    
    def check_inventory(self, b):
        if b in self.bicycles:
            if self.bicycles[b].nowkeep() > 0:
                return True
            else:
                return False
        else:
            return False
    
    def rent_and_fee(self, b, booked_time):
        rentID = self.bicycles[b].rent()
        self.transactions[rentID] = Transaction(rentID, booked_time)
        self.transactions[rentID].start_tracking()
        first_payment = self.bicycles[b].calculate_first_fee(b,booked_time)
        print(f"The ID for this transaction is {rentID}. After promotion, recieved {first_payment:.2f} dollars.")
           
    def return_bike(self, b, ID):
        self.bicycles[b].returnit()
        self.transactions[ID].over = 1
        prompt1='\nBecause this is a proof-of-concept programming, please simulate the time test. \n\
How many hours do you want to simulate to pass from the time the bike was started to rent?'
        prompt2='\nBecause this is a proof-of-concept programming, please simulate the time to test. \n\
How many minutes do you want to simulate to pass from the time the bike was started to rent?'
        hours=get_Integer(prompt1)
        munites=get_Integer(prompt2)
        simulated_time.advance_time(hours,munites)
        # Calculate the used time
        using_time = self.transactions[ID].end_tracking()
        extra_time_in_hours = using_time.total_seconds() / 3600 - self.transactions[ID].booked_time
        # Convert it to timedelta for consistent operations
        extra_time = datetime.timedelta(hours=extra_time_in_hours)
        # Calculate the actual fee. This involves converting the timedelta into hours.
        extra_fee = extra_time.total_seconds() / 3600 * self.bicycles[b].rate * (60 / self.bicycles[b].time_frame)  
        actual_fee = extra_fee + self.bicycles[b].calculate_first_fee(b, self.transactions[ID].booked_time)
        self.fee[ID]=actual_fee
        
        print(f"Successfully returned the {b}. Thank you!")      
        print(f"Additonal fee of ${extra_fee:.2f} for {extra_time_in_hours:.2f} extra hours")
        self.save_transactions_to_csv(f'{simulated_time.get_current_time().strftime("%Y-%m-%d_%H-%M-%S")[0:10]}.csv', ID, b)

    def save_transactions_to_csv(self, filename,ID,b):
        if os.path.exists(filename):
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)

                transaction = self.transactions[ID]
                using_time = transaction.end_tracking() 
                
                writer.writerow([ID,b,self.transactions[ID].start_time.strftime('%Y-%m-%d %H:%M:%S'),self.transactions[ID].end_time.strftime('%Y-%m-%d %H:%M:%S'),using_time.total_seconds() / 60,self.fee[ID]])
            
        else:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['order_no','bike_type', 'start_time', 'end_time', 'using_time','fee']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                transaction = self.transactions[ID]
                using_time = transaction.end_tracking() 
                
                writer.writerow({
                        'order_no': ID,
                        'bike_type':b,
                        'start_time': self.transactions[ID].start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_time': self.transactions[ID].end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'using_time':using_time.total_seconds() / 60,
                        'fee': self.fee[ID]
                    })
       
    def sales_report(self):
        if os.path.exists(f'{simulated_time.get_current_time().strftime("%Y-%m-%d_%H-%M-%S")[0:10]}.csv'):
            df=pd.read_csv(f'{simulated_time.get_current_time().strftime("%Y-%m-%d_%H-%M-%S")[0:10]}.csv')
            #prepare the data
            bike_type=list(df.bike_type.unique())
            # Convert time columns to datetime format
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
    
            # Calculate the using_time as a timedelta
            df['using_time'] = df['end_time'] - df['start_time']
            sales_type=df.groupby('bike_type')['fee'].sum()
            avg_time=df.groupby('bike_type')['using_time'].mean().dt.total_seconds() / 3600
            order_type=df.groupby('bike_type')['order_no'].count()
            print(f"{'bike_type':<20s}  {'sales':>10s}  {'avg_time':>10s}  {'order_qty':>10s}")
            #draw the tabulation
            for c,o,a,s in zip(bike_type,sales_type,avg_time,order_type):
                print(f"{c:<20s} {o:>10.0f}{a:>10.2f}{s:>10.0f}")
            #draw ASCII bar chart
            dict1=order_type.to_dict()
            max_value = max(dict1.values())
            increment = max_value / 25    
            longest_label_length = 20
    
            for key,value in dict1.items():
                bar_chunks, remainder = divmod(int(value * 8 / increment), 8)
                bar = '█' * bar_chunks
                if remainder > 0:
                    bar += chr(ord('█') + (8 - remainder))
                bar = bar or  '▏'
                print(f'{key.rjust(longest_label_length)} ▏ {value:#4d} {bar}')
            #draw bar chart,pie chart
            plt.style.use('ggplot')
            fig=plt.figure(figsize=(10,10))
            fig.suptitle('Sales Analysis',fontsize=16)
            ax1=fig.add_subplot(2,2,1)
            plt.barh(np.arange(5),sales_type,height=0.5,tick_label=bike_type)
            plt.title('Sales')
            #add avg line
            sales_avg=sales_type.mean()
            plt.axvline(x=sales_avg,color='b',linestyle='--',linewidth=3)
            
            ax2=fig.add_subplot(2,2,2)
            plt.barh(np.arange(5),order_type,height=0.5,tick_label=bike_type)
            #add avg line
            order_avg=order_type.mean()
            plt.axvline(x=order_avg,color='b',linestyle='--',linewidth=3)
            
            #pie chart
            fig=plt.figure(figsize=(10,6))
            plt.pie(sales_type,labels=bike_type,
                colors=['g','r','y','c','b'],
                startangle=90,
                autopct='%1.1f%%')
            plt.legend(bike_type)
            plt.legend(loc='center right')
            plt.title('Proportion of Sales by Type')
            plt.axis('equal')
        else:
            print('Now there is no retured bike, thus no transcation record. Please print sales report at least after 1 bike is returned! ')

#client_tier
class client_tier(): 
    def __init__(self):
        self.last_interaction_day = None# To store the last day of interaction
    def start(self):
        while True:
            choice = self.Menu()
            if choice == "A":
                b = input("Bicycle Options:\n\
        - Adult_single\n\
        - Kids\n\
        - Tandem\n\
        - Family\n\
        - Pedal_go_karts\n\
          What type of bicycle do you want to add? ").strip().capitalize()
                if b not in PRICING.keys():
                    print('Please choose a current type of bike!')
                    continue
                BicycleKeeper.add_new_product(b, get_Integer("How many bicycles do you want to add? "))
                print("You have added successfully!")
                
            elif choice == "I":
                print(BicycleKeeper.update_Inventory())
                bikes = BicycleKeeper.display_Inventory()
                print(f'There are {len(bikes)} types of bikes')
                for i in bikes:
                    print(f'There are {bikes[i].adding} {bikes[i].Type} in the Inventory, {bikes[i].nowkeep()} available to rent. ')
            
            elif choice == "P":
                bicycle_type = input("Bicycle Options:\n\
        - Adult_single\n\
        - Kids\n\
        - Tandem\n\
        - Family\n\
        - Pedal_go_karts\n\
          What type of bicycle should be rent? ").strip().capitalize()
                if bicycle_type not in PRICING.keys():
                    print('Please choose a current type of bike!')
                    continue
                if BicycleKeeper.check_inventory(bicycle_type):
                    hours = get_Integer("Enter renting hours (as a whole number): ")
                    minutes = get_Integer("Enter renting minutes (0-60): ", 0, 60)
                    booked_time = hours +(minutes/60)
                    print(f"Renting {bicycle_type} Bike for {booked_time:.2f} hours.")
                    BicycleKeeper.rent_and_fee(bicycle_type, booked_time)
                else:
                    print("For this type, there is no enough bicycle to rent.")
                                
            elif choice == "R":
                bike_type = input("Bicycle Options:\n\
        - Adult_single\n\
        - Kids\n\
        - Tandem\n\
        - Family\n\
        - Pedal_go_karts\n\
          What type of bicycle should be return? ").strip().capitalize()
                if bike_type not in PRICING.keys():
                    print("Invalid bike type.")
                    continue
                rentID = input("Enter the rent ID: ")
                if rentID not in BicycleKeeper.transactions.keys():
                    print("Invalid transaction ID. Please input a valid transaction ID.")
                    continue
                else:
                    if BicycleKeeper.transactions[rentID].over:
                        print("This transaction is over. Please input a valid transaction ID.")
                        continue
                    else:                    
                        BicycleKeeper.return_bike(bike_type, rentID)
                self.check_for_day_change()     
            elif choice == "S":
                BicycleKeeper.sales_report()
                
            elif choice == "Q":
                break
            
            elif choice not in ("A","I","P","R","S","Q"):
                print("Please enter a correct choice!")
                continue
            
#return all bike when a new day starts
    def check_for_day_change(self):
        current_day = simulated_time.get_current_time().date()
        if self.last_interaction_day != current_day:
            self.last_interaction_day = current_day
            self.return_all_bikes()
    
    def return_all_bikes(self):
        print("Automatically returning all rented bikes to inventory.")
        for bike_type in BicycleKeeper.bicycles:
            while BicycleKeeper.bicycles[bike_type].renting > 0:
                BicycleKeeper.bicycles[bike_type].returnit()
                print(f"Returned a {bike_type} bike to inventory.")
                
#menu
    def Menu(self):
        items = "***** Bicycle Rental System *****\n\
        Please update to at least python 3.10\n\
        A. Add New Inventory\n\
        I. Inventory\n\
        P. Rental and Payment\n\
        R. Return Rental\n\
        S: Sales Report Today\n\
        Q: Quit\n"
        print(items)
        choice = input("Please enter your choice: ").upper().strip()
        return choice

# Create an instance of SimulatedTime with a specific starting time
simulated_time = SimulatedTime(initial_time=datetime.datetime(2023, 8, 25, 10, 0))


if __name__ == "__main__":
    BicycleKeeper = Controller()
    BicycleSys = client_tier()
    BicycleSys.start()
