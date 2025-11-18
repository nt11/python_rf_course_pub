
# import sys, pyvisa, time, numpy (example 105), matplotlib (example 106)

def read_trace_find_max(sa):
    # Query the instrument for the trace data (example 111)

    # Read the ASCII data (example 111)

    # Convert the string data to a numpy array (example 111)

    # Get the current frequency settings (example 110 and slide 2-65)
    #start_freq  = ...
    #stop_freq   = ...
    #num_points  = ...

    # Calculate frequency points, use np.linspace (example 111)
    #f = ...

    # Plot the data (example 106 and slide 2-44), use plot, xlabel, ylabel, title,grid ('on'), show

    # Use np.argmax to find the maximum value of the trace (slide 2-42) to find f_peak (the frequency) and y_peak (the power)

    return f_peak, y_peak

if __name__ == "__main__":
    # Make matplot lib interactive (need to change the settings like in slide 2-52 - 2-55, otherwise plots will disappear)
    plt.ion()

    # Connect to the instrument (example 109)
    # rm = ...
    try:
        pass
        #ip = ...
        #sa = ...

        # Query the signal generator name (examle 109)

    except pyvisa.errors.VisaIOError:
        print(f'Failed to connect to the instrument at {ip}')
        sys.exit(1)

    # Reset and clear all status (errors) of the spectrum analyzer (example 109)

    #reset
    #cls

    # Set the spectrum analyzer to maximal span (*)
    sa.write("sense:FREQuency:SPAN:FULL")
    # Set auto resolution bandwidth (*)
    sa.write("sense:BANDwidth:RESolution:AUTO ON")

    # Set the trace to clear/write (example 111 and slide 2-64)
    #sa.write ...

    # Set the sweep mode to continues (*)
    sa.write("INITiate:CONTinuous ON")

    # Wait for the sweep to complete
    # sleep for 2 seconds (example 104)

    # Find the peaks and plot by calling the read_trace_find_max function
    # Fc,p = ...

    # Set the refrence level to the maximum. Compute a desired max level (slightly above the maximum peak) and set it
    # slide 2-65
    #max_level = ...
    #sa.write ...


    # Set the span to 100:10:1:0.1:0.01 MHz (*)
    Fspan = np.logspace(2, -2, 5) # Span in MHz

    # Loop over the spans
        # set the center frequency to the peak frequency and the span to the current span (slide 2-64)
        #sa.write ...
        #sa.write ...

        # sleep for 2 seconds (example 104)

        # Find the peaks and plot by calling the read_trace_find_max function
        #Fc,p = ...

        # print the center frequency, span and peak power (using f-string example 025 and slide 1-130)

        #print(...)

    # Out of the loop...
    # print the last RBW

    # Close the connection (example 109)
    #sa....
    #rm...


        
