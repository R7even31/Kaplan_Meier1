import math 

TEST_S = [(0,1),(5,0.95),(10,0.85),(15,0.75),(20,0.6),(25,0.4),(30,0.25),(35,0.15),(40,0.1),(45,0.05),(50,0)]

def x_t(t):
        return t

def one(t):
    return 1

EXPECTATION_FUNCTIONS = {
    "x_t": x_t, #first moment
    "one": one, #raw integral
}

#NOTE: ALL INTEREST RATES ARE IN PERCENTAGES

INTEREST_RATE_LOW = 1 
INTEREST_RATE_HIGH = 10
INTEREST_RATE_STEP = 0.1 #better models with smaller steps

TARGET_ROR = 5 


def expectation(f,x):
    # f is a numerical function, a list of tuples.
    # x is a function, expectation(f,x) calculates E(x)
    #NOTE: This assumes that points in f are equally spaced.
    y = []
    t = []
    for i,v in f:
        y.append(x(i) * v)
        t.append(i)
    i = 2

    n = len(t) - 1 

    h = (t[-1] - t[0]) / n  # Width of each interval
    integral = y[0] + y[-1]  # Start with first and last y values

    #simpsons 1/3 rule
    for i in range(1, n, 2):  # Odd indices
        integral += 4 * y[i]
    for i in range(2, n, 2):  # Even indices
        integral += 2 * y[i]

    return integral * h /3


class LifeInsurance:
    def __init__(self, s, payout):
        self.s = s # s is the survival function
        self.payout = payout #npv of payout evaluated at time of payout
        self.cached_lifetime = None
        self.payment = 1600 # this is what we want to calculate
        #NOTE: payment is considered a flat annuity-immediate with period 1 month

    def annuity_multiplier(self,i): #TODO: Subtract cash value from payments.
        e = self.expected_lifetime()
        i_12 = i / 12
       
        v_12 = 1/(1 + i_12)
    
        return (1 - (v_12 ** math.floor(e * 12)))/i_12

    #cache expected lifetime for performance, if s is changed, cache must be cleared.
    def expected_lifetime(self):
        if self.cached_lifetime == None: 
            

            self.cached_lifetime = expectation(self.s, EXPECTATION_FUNCTIONS["one"])
        return self.cached_lifetime

    def e_npv(self,i):
        e = self.expected_lifetime()
        v = 1/(1 + i)
       
        npv_pmt = self.payment * self.annuity_multiplier(i) #annuity-immediate npv
        npv_payout = self.payout * (v ** e)
        return npv_pmt - npv_payout

    def modified_duration(self,i):
        e = self.expected_lifetime()
        a = self.annuity_multiplier(i)
        npv = self.e_npv(i)
        return -(1/npv) * a

    def convexity(self,i):
        return - self.e_npv(i) * self.modified_duration(i)

    def rate_of_return(self):
        initial_guess = 0.07
        t = initial_guess
        y = self.e_npv(t)
        while abs(y) > 0.00001: #Newtons method
            dy_dt = self.annuity_multiplier(t)
            y = self.e_npv(t)
            t -= y/dy_dt
        return t


test = LifeInsurance(TEST_S,1000000)
test_i = 0.07
print("life expectancy:")
print(test.expected_lifetime())
print("annuity multiplier:")
print(test.annuity_multiplier(test_i))
print("npv:")
print(test.e_npv(test_i))
print("modified duration:")
print(test.modified_duration(test_i))
print("convexity:")
print(test.convexity(test_i))
print("ror:")
print(test.rate_of_return())

