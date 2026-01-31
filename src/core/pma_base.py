class PMActivity:
    def __init__(self, df):
        self.activity_timeseries  = df
        self.measbegin_datetime   = None
        self.measbegin_date       = None
        self.measbegin_time       = None
        self.measend_datetime     = None
        self.measend_date         = None
        self.measend_time         = None
        self.meas_days            = None
        self.meas_minutes         = None

        self._calc_time_series_props()

    def _calc_time_series_props(self):
        acty = self.activity_timeseries.loc[:,['timestamp', 'activity']]
        self.measbegin_datetime   = acty.iloc[ 0,:][0]
        self.measend_datetime     = acty.iloc[-1,:][0]

class PMAPerson:
    def __init__(self, id, age, gender):
        self.id         = id
        self.age        = age
        self.gender     = gender
        self.diag       = None
        self.activity   = None

    def __repr__(self):
        return f"id={self.id} age={self.age}"

class PMADataADHDKaggle(PMAPerson):
    def __init__(self, id, agebin, gender):
        self.id       = id
        self.agemin   = int(agebin.split('-')[0])
        self.agemax   = int(agebin.split('-')[1])
        self.age      = (self.agemax+self.agemin)//2
        self.gender   = gender
        
    
# test
dir_data_raw='../../data/raw/psychiatric-motor-activity-dataset/'
dis = 'adhd'
print(dis)
#dis = 'depression'
#dis = 'schizophrenia'
#dis = 'clinic'
#dis = 'control'
pat = '1'
#import os
#os.listdir(dir_data_raw + dis + '/')
#filename=#
import pandas as pd
df = pd.read_csv(dir_data_raw + dis + '/' + dis + '_' + pat + '.csv')
print(df.head())

bla=PMActivity(df)
print(bla.measbegin_datetime)
print(bla.measend_datetime)

