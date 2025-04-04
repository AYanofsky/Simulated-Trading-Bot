April 3, 2025
I want to make a bot which is capable of analyzing a non-mainstream stock which gained a significant amount of market cap, then (somewhat nebulously) figure out if it will fail or not. If it expects it to fail, I want the bot to enter a short position and sell once a certain percentage of profit has been reached. Otherwise, the bot should leave the stock alone. I will probably program it to see if something is falling first and short if it is falling first.

So far I've realized that the speed of the API's HTTP/S connections is a seriously limiting factor when dealing with large quantities of tickers. I'm going to try to write a web scraper to grab data for me.


April 4, 2025
I was up very late last night trying to get this thing to spit numbers out at me.
I fixed a bunch of bugs, and right now the bot is capable of detecting a breakout based on moving average and a static percentage. It can also detect breakdowns.
Today I implemented a trailing stop-loss.

I branched the repo to refactor the algorithm to focus primarily on backtesting and improving it.