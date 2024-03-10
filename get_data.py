
import pymongo 
import certifi


def timestamp_to_millis(timestamp_str):
    hh, mm, ss, mmm = map(int, timestamp_str.split(':'))
    return (hh * 3600 + mm * 60 + ss) * 1000 + mmm




class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self,user_name="SenseORAN",password="SenseORANFeb21",cluster="orancluster.5njsvyr"):
        if hasattr(self, 'uri'):  # Check if instance already initialized
            return
        
        self.uri = f'mongodb+srv://{user_name}:{password}@{cluster}.mongodb.net/?retryWrites=true&w=majority'
        self.client = pymongo.MongoClient(self.uri,tlsCAFile = certifi.where())

        self.current_timestamp = 0

        self.load_csv()
        self.load_log_file()

        self.scheduling_policy_map = {
            0:"Round Robin",
            1:"Water Filling",
            2:"Proportionally Fair"
        }
    

    def load_log_file(self,db_name='log_file'):
        self.db = self.client[db_name]
        for row in self.db['log'].find():
            data = sorted(row['entries'], key=lambda x: x['unix_epoch'])
        
        self.log_data = {}
        for record in data:
            timestamp = timestamp_to_millis(record['readable_timestamp'].split(' ')[1])
            self.log_data[timestamp] = record['class']
        

    def load_other_csv_columns(self,db,column_name):
        output_dic = {}
        for row in db[column_name].find():
            data = sorted(row['data'], key=lambda x: x['unix_epoch'])
        
        for record in data:
            timestamp = timestamp_to_millis(record['readable_timestamp'].split(' ')[1])
            output_dic[timestamp] = record['value']
        
        return output_dic
    

    def format_column_name(self,column_name):
        column_name = column_name.replace('sum_','').replace(' [Mbps]','').replace('_',' ')
        word_groups = column_name.split(" ")

        
        
        
        for i in range(len(word_groups)):
            #All these words should be completely capialized like SINR
            if word_groups[i] in ['rx','ul','prb','tx','sinr','mcs']:
                word_groups[i] = word_groups[i].upper()
            else:
                word_groups[i] = word_groups[i][0].upper() + word_groups[i][1:]
        
        if 'Prbs' in word_groups:
            return 'PRB '+word_groups[0]
        
        return " ".join(word_groups)
      

    def load_csv(self,db_name='csv'):
        self.db = self.client[db_name]
        
        self.graph_columns = ["rx_brate uplink [Mbps]","ul_sinr",
           "sum_requested_prbs","tx_brate downlink [Mbps]",
           "ul_mcs","sum_granted_prbs"]
        
        self.graph_x_values = {}
        self.graph_y_values = {}

        for column_name in self.graph_columns:
            column = self.db[column_name]
            for row in column.find():
                data = sorted(row['data'], key=lambda x: x['unix_epoch'])
            
            self.graph_x_values[self.format_column_name(column_name)] = [timestamp_to_millis(timestamp['readable_timestamp'].split(' ')[1]) for timestamp in data]
            self.graph_y_values[self.format_column_name(column_name)] = [signal_value['value'] for signal_value in data]

        self.rbs_assigned = self.load_other_csv_columns(self.db,'slice_prb')

        self.scheduling_policy = self.load_other_csv_columns(self.db,'scheduling_policy')
        self.graph_columns = [self.format_column_name(column_name) for column_name in self.graph_columns]
        
    def map_scheduling_policy(self,policy):
        if policy == "":
            return ""

        
        return self.scheduling_policy_map[policy]
        



    def get_graph_values(self):
        return self.graph_x_values,self.graph_y_values

    def get_graph_columns(self):
        return self.graph_columns

    def get_rbs_assigned(self):
        return self.rbs_assigned
    
    def set_current_timestamp(self,timestamp):
        self.current_timestamp = timestamp

