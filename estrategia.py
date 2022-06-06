class FormalOrangeCobra(QCAlgorithm):
    def Initialize(self):

        self.SetStartDate(2022,1,1) #Fecha de Inicio
        self.SetEndDate(2021,5,30) #Fecha Fin
        self.SetCash(10000)  #Cash Inicial  

        self.UniverseSettings.Resolution = Resolution.Daily
        
        self.AddEquity("SPY",Resolution.Daily)
        
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        
        self.Schedule.On(self.DateRules.EveryDay("SPY"), \
                        self.TimeRules.BeforeMarketClose("SPY", 3), \
                        self.EveryDayBeforeMarketClose)

        self.__numberOfSymbols = 1000 #Numero de acciones que pasamos en el primer filtro
        self.__numberOfSymbolsFine = 5 #Acciones con las que nos quedamos
        self._changes = None
        self.market_cap = {}

    def CoarseSelectionFunction(self, coarse):
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        return [ x.Symbol for x in sortedByDollarVolume[:self.__numberOfSymbols] if x.HasFundamentalData]

    def FineSelectionFunction(self, fine):
        for i in fine:
            self.market_cap[i] = (i.EarningReports.BasicAverageShares.ThreeMonths *
            i.EarningReports.BasicEPS.TwelveMonths *
            i.ValuationRatios.PERatio)

        sorted_market_cap = sorted([x for x in fine if self.market_cap[x] > 0], key=lambda x: self.market_cap[x])
        return [ x.Symbol for x in sorted_market_cap[:self.__numberOfSymbolsFine]]

    def OnData(self, data):
        pass
    
    def EveryDayBeforeMarketClose(self):
        self.Liquidate()
        if self._changes is None: return

        for security in self._changes.AddedSecurities:
            self.SetHoldings(security.Symbol, -(1/len(self._changes.AddedSecurities)))
            

        self._changes = None
    
    def OnSecuritiesChanged(self, changes):
        self._changes = changes