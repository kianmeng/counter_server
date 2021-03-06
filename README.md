License.
--------
Except the README.md, all python source codes are licensed under the GPL3
license.

About
-----
Create a TCP server (in your language of choice) that implements a text based
protocol for managing counters.

1. Counters are integers that have label.
2. Counters can only be incremented. 
3. The counter's value resets every minute. However, previous values of the
   counter must be kept. 
4. If no increments took place during a particular minute, the value for that
   minute is 0.

Commands that the TCP server should accept:

1. CREATE_COUNTER - Parameters: label of the counter to create
2. INCREMENT_COUNTER - Parameters: label of the counter to increment
3. GET_COUNTER_VALUES - Parameters: label of the counter, from date, to date -
   this should return value of the counter between that date range, if the date
   range is an hour long, then it should return 60 values for the counter.
4. AVERAGE_COUNTER_VALUE - Parameters: label of the counter, from_date, to_date
   - returns the average value of the counter during that date range.
