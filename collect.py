# %% 
import argparse
import fastf1
import pandas as pd 
import time

pd.set_option('display.max_columns', None)

# %%
class collectResults:

    def __init__(self, years=[2021,2022,2023], modes=['R', 'S']):
        self.years = years 
        self.modes = modes 
        
    def get_data(self, year, gp, mode) -> pd.DataFrame:
        try:
            session = fastf1.get_session(year, gp, mode)

        except ValueError as err: 
            return pd.DataFrame()

        session._load_drivers_results()

        df = session.results
        df['Mode'] = mode
        df['Year'] = session.date.year
        df['Date'] = session.date
        df['RoundNumber'] = session.event['RoundNumber']
        df['OfficialEventName'] = session.event['OfficialEventName']
        df['EventName'] = session.event['EventName']
        df['Country'] = session.event['Country']
        df['Location'] = session.event['Location']
        
        return df

    def save_data(self, df, year, gp, mode):
        filename = f'data/{year}_{gp:02}_{mode}.parquet'
        df.to_parquet(filename, index=False)

    def process(self, year, gp, mode):
        df = self.get_data(year, gp, mode)
        
        if df.empty:
            return False
        
        self.save_data(df, year, gp, mode)
        time.sleep(1)
        return True


    def process_year_modes(self, year):
        try:
            schedule = fastf1.get_event_schedule(year, include_testing=False)
        except Exception:
            print(f"  Não foi possível obter o calendário do ano {year}")
            return

        
        for _, event in schedule.iterrows():
            gp = int(event["RoundNumber"])
            for mode in self.modes:
                self.process(year, gp, mode)
                
    def process_years(self):
        for year in self.years:
            print(f'Coletando dados de {year}')
            self.process_year_modes(year)
            time.sleep(10)

# %% 
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--stop', type=int, default=0)
    parser.add_argument('--years', '-y', nargs='+', type=int)
    parser.add_argument('--modes', '-m', nargs='+')
    
    args = parser.parse_args()

    if args.years:
        collect = collectResults(args.years, args.modes)
    
    elif args.start and args.stop:        
        years = [i for i in range(args.start, args.stop)]
        collect = collectResults(years, args.modes)
    

    collect.process_years()
