import pandas as pd
import seaborn as sns
import panel as pn
import matplotlib.pyplot as plt
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
from datetime import datetime

# TODO: Add docstrings where necessary
# TODO: Implement functions that aren't implemented


def calculate_today_mjd():
    """Computation to find MJD from current datetime

    Return
    ------
    np.float64

    """
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour

    # Formula taken from: https://gssc.esa.int/navipedia/index.php/Julian_Date
    jd = int(365.25 * year) + int(30.6001 * (month + 1)) + day + hour / 24.0 + 1720981.5

    mjd = round(jd - 2400000.5)

    return mjd


def is_mjd(series: pd.Series) -> bool:
    """Check to see if values in series is in MJD format."""
    if not is_numeric_dtype(series):
        return False

    values = series

    mjd_start = 0  # zero value to represent epoch. 12:00 January 1, 4713 BC
    mjd_curr = calculate_today_mjd()

    if (series > mjd_start) and (series <= mjd_curr):
        return True
    else:
        return False
    raise NotImplementedError


def populate_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add necessary columns and rows into the dataframe populated with necessary data
    to allow for simple analysis.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame object to perform operations on.

    Return
    ------
    pd.DataFrame
        Modified dataframe object
    """

    first_col = df.iloc[:, 0]

    # Conversion from '.txt' to a 'pandas.DataFrame' causes values to lose precision by 1e-3,
    # this condition corrects that
    if first_col.lt(1).all():
        first_col = first_col.apply(lambda x: x * 1e1)

    if first_col.gt(10).all():
        first_col = first_col.apply(lambda x: x * 1e-2)

    df.iloc[:, 0] = first_col

    # Add arbritrary datetime range column to data
    start_time = pd.to_datetime("1997-01-01 08:00:00")
    df.index.names = ["DataPoint"]
    df["time"] = pd.date_range(start=start_time, periods=len(df), freq="BMS")

    return df


def convert_to_datetime(series: pd.Series) -> pd.Series:
    """Converts pandas series time column to ISO 8601 standard....

    Parameters
    ----------
    series: pd.Series
        Series object to perform operations on.

    Return
    ------
    pd.Series
        Modified pd.Series object

    Notes
    -----
    A standard for timestamped data.

    References
    ----------
    .. [1] International Organization for Standardization, "ISO 8601 Date and time format".
        https://www.iso.org/iso-8601-date-and-time-format.html
    """
    if not is_datetime64_any_dtype(series):
        raise ValueError("Column does not exist, or data is not the correct type.")

    # Difficult to determine as to whether the values are in MJD format as the types would be either float, or int
    if isinstance(series, float) | isinstance(series, int):
        series = pd.to_datetime(series)
        return series

    series = pd.DatetimeIndex(series).to_julian_date()
    # return series
    raise NotImplementedError


# TODO: Add check for DataFrame to ensure 'time' column exists.
def convert_to_mjd(df: pd.DataFrame) -> pd.DataFrame:
    """Converts DataFrame with 'time' column to Modified Julian Date (MJD).

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame with 'time' column

    Return
    ------
    pd.DataFrame
        Modified ppd.DataFrame object

    Notes
    -----
    MJD is a modification of the Julian Date that is routinely used by astronomers, geodists, and even some historians.
    MJD = JD - 2400000.5

    References
    --------
    .. [1] NASA Goddard Space Flight Center, "Modified Julian Dates".
        https://core2.gsfc.nasa.gov/time/

    """
    series = df["time"]
    if is_datetime64_any_dtype(series):
        mjd = pd.DatetimeIndex(series).to_julian_date() - 2400000.5

    df["time"] = mjd

    return df


def generate_pane(df: pd.DataFrame):
    """Plots the values of the DataFrame into a matplotlib figure,
    to then be used as a pane within a panel template.

    Parameters
    ----------
    df: pd.DataFrame

    """

    df = populate_df(df)

    x = df.index
    y = df["Frequency"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlabel("Data Point")
    sns.lineplot(data=df, x=x, y=y, dashes=True, linewidth=2.5, ax=ax)

    pane = pn.pane.Matplotlib(fig, tight=True)
    return pane
