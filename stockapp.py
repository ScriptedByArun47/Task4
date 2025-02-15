#stage : finaly
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# UI Design
KV = '''
<SearchBox>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "60dp"

    MDCard:
        radius: [15, 15, 15, 15]
        md_bg_color: 0.15, 0.15, 0.15, 1  # Darker search background
        padding: "10dp"
        size_hint_x: 1
        size_hint_y: None
        height: "48dp"
        elevation: 4

        MDTextField:
            id: search_field
            hint_text: "Enter stock symbol..."
            size_hint_x: 1
            size_hint_y: None
            height: "48dp"
            mode: "fill"
            fill_color: 0.15, 0.15, 0.15, 1  # Darker fill color
            line_color_focus: 118/255, 139/255, 253/255, 1  # Focus color
            text_color: 1, 1, 1, 1  # White text
            font_size: "18sp"
            radius: [10, 10, 10, 10]

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.121, 0.125, 0.145, 1  # Dark background
        Rectangle:
            pos: self.pos
            size: self.size

    MDTopAppBar:
        title: "Stock Market"
        md_bg_color: 0.462, 0.545, 0.992, 1

        elevation: 4
        left_action_items: [["magnify", lambda x: app.show_search_dialog()]]
        right_action_items: [["refresh", lambda x: app.load_stock_prices()]]

    ScrollView:
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            adaptive_height: True

            # Brokerage Account Section
            MDCard:
                orientation: 'vertical'
                padding: dp(15)
                size_hint_y: None
                height: dp(100)
                radius: [20, 20, 20, 20]
                md_bg_color: 1, 1, 1, 1

                MDLabel:
                    text: "Brokerage Account"
                    font_style: "Subtitle1"
                    theme_text_color: "Primary"
                    bold:True

                MDLabel:
                    id: balance_label
                    text: "$17,159.5"
                    font_style: "H6"
                    bold:False

            # Live Stock Trends Section
            MDCard:
                orientation: 'vertical'
                padding: dp(15)
                size_hint_y: None
                height: dp(300)
                radius: [20, 20, 20, 20]
                md_bg_color: 1, 1, 1, 1

                MDLabel:
                    text: "Live Stock Trends"
                    font_style: "Subtitle1"
                    theme_text_color: "Secondary"

                BoxLayout:
                    id: graph_box
                    size_hint_y: 1

            # Stock List Section
            MDLabel:
                text: "Stocks"
                font_style: "H6"
                bold: True
                padding: dp(15)

            MDList:
                id: stock_list
                md_bg_color: 1, 1, 1, 1
'''
class SearchBox(BoxLayout):
    pass

class StockMarketApp(MDApp):
    search_dialog = None
    stock_symbols = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        self.load_stock_prices()
        self.update_graph()
        Clock.schedule_interval(self.update_graph, 60)  # Update every 60 seconds

    def load_stock_prices(self):
        stock_list = self.root.ids.stock_list
        stock_list.clear_widgets()
        for symbol in self.stock_symbols:
            stock_data = yf.Ticker(symbol).history(period="5d")
            if not stock_data.empty:
                stock_price = stock_data["Close"].iloc[-1]
                item = OneLineListItem(text=f"{symbol} - ${stock_price:.2f}")
                stock_list.add_widget(item)

    def update_graph(self, *args):
        self.root.ids.graph_box.clear_widgets()
        plt.clf()

        fig, ax = plt.subplots(figsize=(6, 3))
        
        for symbol in self.stock_symbols:  # Plot all stocks added
            stock_data = yf.Ticker(symbol).history(period="5d")
            stock_prices = stock_data["Close"]
            if len(stock_prices) > 1:
                percentage_change = ((stock_prices - stock_prices.iloc[0]) / stock_prices.iloc[0]) * 100
                ax.plot(stock_prices.index, percentage_change, label=symbol)
        
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.legend()
        ax.set_title("Stock Market Trends (Live)")
        ax.set_xlabel("Time")
        ax.set_ylabel("% Change")
        
        self.root.ids.graph_box.add_widget(FigureCanvasKivyAgg(fig))

    def show_search_dialog(self):
        if not self.search_dialog:
            self.search_box = MDTextField(hint_text="Enter stock symbol..."
            )
            self.search_dialog = MDDialog(
                title="Search Stock",
                type="custom",
                content_cls=self.search_box,
                buttons=[
                    MDRaisedButton(text="Search", on_release=self.search_stock)
                ],
            )
        self.search_dialog.open()

    def search_stock(self, *args):
        stock_symbol = self.search_box.text.strip().upper()
        if stock_symbol and stock_symbol not in self.stock_symbols:
            self.stock_symbols.append(stock_symbol)
            self.load_stock_prices()
            self.update_graph()
        if self.search_dialog:
            self.search_dialog.dismiss()

if __name__ == "__main__":
    StockMarketApp().run()
