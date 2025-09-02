import io
import panel as pn
import pandas as pd
import seaborn as sns

from pathlib import Path

from src.dfops import (
    convert_to_mjd,
    add_time_to_df,
    generate_pane,
)

PROJ_ROOT = Path(__file__).parent.parent

TST_FPATH = PROJ_ROOT / "data" / "tst_suit.txt"
NBS_FPATH = PROJ_ROOT / "data" / "nbs.txt"

# DataFrames contain only a single column
TST_DF = pd.read_csv(TST_FPATH, sep=",", names=["Frequency"])
NBS_DF = pd.read_csv(NBS_FPATH, sep=",", names=["Frequency"])


pn.extension("tabulator")
sns.set_theme(style="whitegrid")

# TODO: fix datetime conversion when "convert to JD" is pressed, converted values is not accurate


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class PnGui:
    """Layout objects for the gui to include certain functions"""

    def __init__(self):
        self.tst_df = populate_df(TST_DF)
        self.nbs_df = populate_df(NBS_DF)

        self.tst_tab = pn.widgets.Tabulator(self.tst_df, height=500)
        self.nbs_tab = pn.widgets.Tabulator(self.nbs_df)

        self.template = pn.template.FastListTemplate(title="Psuedo data experiment")

        self.tst_pane = generate_pane(TST_DF)
        self.nbs_pane = generate_pane(NBS_DF)

        self.tst_convert_btn = pn.widgets.Button(
            name="Convert time to MJD", button_type="primary"
        )

        def update_tst_time(event):
            # The floats rendered is formatted with 'Numeral.js', this fixes the formatting
            self.tst_tab.formatters = {
                "time": {"type": "number", "format": "0.0000000000"}
            }
            self.tst_tab.value = convert_to_mjd(self.tst_tab.value)

        self.tst_convert_btn.on_click(update_tst_time)

        def generate_tst_csv():
            df = self.tst_tab.value
            buffer = io.StringIO()
            df.to_csv(buffer, index=True)
            buffer.seek(0)
            return buffer

        self.tst_download_btn = pn.widgets.FileDownload(
            callback=generate_tst_csv,
            auto=True,
            file="test_suite_data.csv",
            button_type="success",
        )

        self.nbs_convert_btn = pn.widgets.Button(
            name="Convert time to MJD", button_type="primary"
        )

        def update_nbs_time(event):
            self.nbs_tab.formatters = {
                "time": {"type": "number", "format": "0.0000000000"}
            }
            self.nbs_tab.value = convert_to_mjd(self.nbs_tab.value)

        self.nbs_convert_btn.on_click(update_nbs_time)

        def generate_nbs_csv():
            df = self.nbs_tab.value
            buffer = io.StringIO()
            df.to_csv(buffer, index=True)
            buffer.seek(0)
            return buffer

        self.nbs_download_btn = pn.widgets.FileDownload(
            callback=generate_nbs_csv,
            auto=True,
            file="nbs_data.csv",
            button_type="success",
        )

        self.tst_btn_row = pn.Row(self.tst_convert_btn, self.tst_download_btn)
        self.nbs_btn_row = pn.Row(self.nbs_convert_btn, self.nbs_download_btn)

        self.tst_tab_column = pn.Column(self.tst_btn_row, self.tst_tab)
        self.nbs_tab_column = pn.Column(self.nbs_btn_row, self.nbs_tab)

        self.tst_row = pn.Row(self.tst_pane, self.tst_tab_column)
        self.nbs_row = pn.Row(self.nbs_pane, self.nbs_tab_column)

        self.tst_card = pn.Card(
            self.tst_row, collapsed=False, collapsible=True, title="Test Suite Data"
        )
        self.nbs_card = pn.Card(
            self.nbs_row, collapsed=False, collapsible=True, title="NBS Data"
        )

        self.card_row = pn.Row(self.tst_card, self.nbs_card, scroll=True)
        self.template.main.extend([self.card_row])

        self.template.show(
            port=1234,
            address="0.0.0.0",
            websocket_origin=["*"],
            threaded=True,
            verbose=True,
            open=True,
        )
