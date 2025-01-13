import os
for year in range(2020,2025):
	for month in range(1,13):
		date = f'{year:04d}{month:02d}__'
		print(date)
		os.mkdir(date)