
from get_data  import Database
from bokeh.models import Div
database = Database()




def scheduling_policy(doc):
    data = database.scheduling_policy
    
    
    def update():
        # Directly modify the text of 'div'
        
        policy = database.map_scheduling_policy(data.get(database.current_timestamp,""))
        div.text = policy
        #print(data)
        


    # Initialize 'div' here so that it's in the scope of 'update'
    div = Div(text="")
    

    doc.add_root(div)
    doc.add_periodic_callback(update, 500)  # Update every 250 ms