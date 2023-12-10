import pandas as pd
import networkx as nx

def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['id_start'], row['id_end'], weight=row['distance'])

    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G))

    locations = sorted(set(df['id_start']) | set(df['id_end']))
    distance_matrix = pd.DataFrame(index=locations, columns=locations)

    for start_loc in locations:
        for end_loc in locations:
            if start_loc == end_loc:
                distance_matrix.loc[start_loc, end_loc] = 0
            elif start_loc in shortest_paths and end_loc in shortest_paths[start_loc]:
                distance_matrix.loc[start_loc, end_loc] = shortest_paths[start_loc][end_loc]
            else:
                distance_matrix.loc[start_loc, end_loc] = float('nan')

    return distance_matrix



def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    distance_matrix_reset = distance_matrix.reset_index()

    unrolled_df = pd.melt(distance_matrix_reset, id_vars='index', var_name='id_end', value_name='distance')

    unrolled_df.columns = ['id_start', 'id_end', 'distance']

    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    unrolled_df.reset_index(drop=True, inplace=True)

    return unrolled_df

result_distance_matrix = calculate_distance_matrix(df)
unrolled_df = unroll_distance_matrix(result_distance_matrix)
print(unrolled_df)


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    reference_df = df[df['id_start'] == reference_id]

    avg_distance = reference_df['distance'].mean()

    lower_threshold = avg_distance - (avg_distance * 0.1)
    upper_threshold = avg_distance + (avg_distance * 0.1)

    within_threshold_df = df[(df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]

    result_ids = within_threshold_df['id_start'].unique()
    result_ids.sort()

    return result_ids

unrolled_df = unroll_distance_matrix(result_distance_matrix)
reference_id = 1  
result_ids = find_ids_within_ten_percentage_threshold(unrolled_df, reference_id)
print(result_ids)


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here

    rate_coefficients = {
        'moto': 0.8,
        'car': 1.2,
        'rv': 1.5,
        'bus': 2.2,
        'truck': 3.6
    }

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        column_name = f'{vehicle_type}'
        df[column_name] = df['distance'] * rate_coefficient

    return df

unrolled_df = unroll_distance_matrix(result_distance_matrix)
result_with_toll_rates = calculate_toll_rate(unrolled_df)
print(result_with_toll_rates)



def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    weekday_time_ranges = [(time(0, 0), time(10, 0)), (time(10, 0), time(18, 0)), (time(18, 0), time(23, 59, 59))]
        weekend_time_ranges = [(time(0, 0), time(23, 59, 59))]
        weekday_discount_factors = [0.8, 1.2, 0.8]
        weekend_discount_factor = 0.7

        # Create new columns for start_day, start_time, end_day, and end_time
        df['start_day'] = df['start_datetime'].dt.day_name()
        df['end_day'] = df['end_datetime'].dt.day_name()
        df['start_time'] = df['start_datetime'].dt.time
        df['end_time'] = df['end_datetime'].dt.time

        # Calculate toll rates based on time ranges and discount factors
        for i, (start_range, end_range) in enumerate(weekday_time_ranges):
            weekday_mask = ((df['start_datetime'].dt.time >= start_range) & (df['start_datetime'].dt.time < end_range) &
                            (df['end_datetime'].dt.time >= start_range) & (df['end_datetime'].dt.time < end_range) &
                            (df['start_datetime'].dt.weekday < 5))  # Weekdays

            df.loc[weekday_mask, ['moto_toll', 'car_toll', 'rv_toll', 'bus_toll', 'truck_toll']] *= weekday_discount_factors[i]

        for start_range, end_range in weekend_time_ranges:
            weekend_mask = ((df['start_datetime'].dt.time >= start_range) & (df['start_datetime'].dt.time <= end_range) &
                            (df['end_datetime'].dt.time >= start_range) & (df['end_datetime'].dt.time <= end_range) &
                            (df['start_datetime'].dt.weekday >= 5))  # Weekends

            df.loc[weekend_mask, ['moto_toll', 'car_toll', 'rv_toll', 'bus_toll', 'truck_toll']] *= weekend_discount_factor

        # Find reference value for the first (id_start, id_end) pair
        reference_value = df.loc[df.index[0], 'id_start']

        # Use find_ids_within_ten_percentage_threshold to get IDs within 10% of the reference value
        ids_within_threshold = find_ids_within_ten_percentage_threshold(df, reference_value)

        return df

result_distance_matrix = calculate_distance_matrix(df)
unrolled_df = unroll_distance_matrix(result_distance_matrix)
result_with_time_based_toll_rates = calculate_time_based_toll_rates(unrolled_df)
print(result_with_time_based_toll_rates)
     