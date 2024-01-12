# Order-book Visualizer using Dash 

In this project, I tried to visualise the everyday order-book we come across on trading platforms and they way they beautifully show us the bid and ask prices using aggregation, decimal precision, colours and even that cool colour bar that increases and decreases in width with respect to the quantity of the instrument available to buy/sell at that given price. 

#### How?
I've used **Plotly Dash** in python to achieve this goal of visualization coupled with a bit of css ( again, through Dash itself ).
The data is coming in from **Binance REST API** and refreshes every 3s ( set by me ) - *my goal here was processing the data and visualizing it, not ultra low latency*
The data is processed using **pandas** dataframes. 

#### Why?
Because why not? I've been trading the forex and crypto market for more than 4 years now. Although I'm not the best trader out there ( I'm working on it :joy: ), I loved the visualisations we are 
provided with. And I wanted to do it myself! 
#### Lets see it?
Sure!

https://github.com/justAcoderguy/OrderBook-Visualization/assets/52568587/df5635cc-17ab-4c19-82cd-585741c567df
