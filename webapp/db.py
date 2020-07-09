from firebase import firebase

# Posting data
firebase = firebase.FirebaseApplication('https://breakthrough-listen-sandbox.firebaseio.com/', None)
data =  { 'Message': 'test_send_one'}
result = firebase.post('/breakthrough-listen-sandbox/flask_vars',data)


# Reading in data
retrieved = firebase.get('/breakthrough-listen-sandbox/flask_vars', '')
print(retrieved)

# Updating Data

retrieved = firebase.put('/breakthrough-listen-sandbox/flask_vars/-MBkt_yIVsUfiHB4WF7c', 'Message', 'Bob')
print('Updated database')


# Delete data 
retrieved = firebase.delete('/breakthrough-listen-sandbox/flask_vars/', '-MBkt_yIVsUfiHB4WF7c')
print('Deleted Record')

# Full video here https://www.youtube.com/watch?v=rKuGCQda_Qo 