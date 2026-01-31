class PMActivity:
    def __init__(self, df):
        self.activity_timeseries = df
        self.meas_begin_datetime = None
        self.meas_begin_date = None
        self.meas_begin_time = None
        self.meas_end_datetime = None
        self.meas_end_date = None
        self.meas_end_time = None
        #
        self.meas_duration = None
        self.meas_days = None
        self.meas_minutes = None
        self.meas_minutes_to_12pm = None

        self._calc_time_series_props()

    def _calc_time_series_props(self):
        acty = self.activity_timeseries.loc[:, ["timestamp", "activity"]]
        self.meas_begin_datetime = acty.iloc[0, 0]
        self.meas_end_datetime = acty.iloc[-1, 0]
        self.meas_begin_date = self.meas_begin_datetime.date()
        self.meas_end_date = self.meas_end_datetime.date()
        self.meas_begin_time = self.meas_begin_datetime.time()
        self.meas_end_time = self.meas_end_datetime.time()
        self.meas_duration = self.meas_end_datetime - self.meas_begin_datetime
        self.meas_minutes = self.meas_duration.total_seconds() // 60
        self.meas_days = self.meas_minutes / 1440
        self.meas_minutes_to_12pm = (
            1440 - self.meas_begin_time.hour * 60 - self.meas_begin_time.minute
        )

    def ordered_activity_24h(self, day=0, offset_minutes=0):
        start_index = 1440 * day + offset_minutes
        end_index = 1440 * (day + 1) + offset_minutes
        return sorted(
            self.activity_timeseries.loc[start_index:end_index, "activity"],
            reverse=True,
        )

    def plot_ordered_activity_24h(self, ax):
        ax.plot(self.ordered_activity_24h(0, 0))


class PMAPerson:
    def __init__(self, id, age, gender):
        self.id = id
        self.age = age
        self.gender = gender
        self.diag = None
        self.activity = None

    def __repr__(self):
        return f"id={self.id} age={self.age}"


class PMADataADHDKaggle(PMAPerson):
    def __init__(self, id, agebin, gender):
        self.id = id
        self.agemin = int(agebin.split("-")[0])
        self.agemax = int(agebin.split("-")[1])
        self.age = (self.agemax + self.agemin) // 2
        self.gender = gender


if __name__ == "__main__":
    # some code for tests
    dir_data_raw = "../../data/raw/psychiatric-motor-activity-dataset/"
    dis = "adhd"
    print(dis)
    # dis = 'depression'
    # dis = 'schizophrenia'
    # dis = 'clinic'
    # dis = 'control'
    pat = "1"
    # import os
    # os.listdir(dir_data_raw + dis + '/')
    # filename=#
    import pandas as pd

    acty_rawfile = dir_data_raw + dis + "/" + dis + "_" + pat + ".csv"
    df = pd.read_csv(acty_rawfile, parse_dates=["timestamp"])
    print(df.head())

    bla = PMActivity(df)
    print(type(bla.meas_begin_time.minute))
    print(bla.meas_end_datetime)
    print(bla.meas_duration.days)
    print(bla.meas_duration)
    print(bla.meas_days)
    print(bla.meas_minutes)
    print(bla.meas_minutes_to_12pm)

    print(bla.ordered_activity_24h()[0:20])
