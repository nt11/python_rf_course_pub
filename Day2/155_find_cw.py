import  sys
import  time
import  numpy as np
import  logging

# module-level logger
logger = logging.getLogger(__name__)

# Import from the course utilities package
from python_rf_course_utils.scpi import SCPIWrapper


def read_max_peak(sa):
    """
    Read maximum peak using marker with comprehensive error handling.
    This function is specific to finding CW signals on spectrum analyzers.

    Args:
        sa: VISA instrument object (raw instrument, not wrapper)

    Returns:
        tuple: (success: bool, frequency_mhz: float or None, power_dbm: float or None)
    """
    try:
        # Set marker to maximum peak
        sa.write("CALC:MARK:MAX")
        time.sleep(0.01)

        # Query the marker frequency
        f_hz = float(sa.query("CALC:MARK:X?").strip())

        # Query the marker power
        p_dbm = float(sa.query("CALC:MARK:Y?").strip())

        # Convert frequency to MHz
        f_mhz = f_hz * 1e-6

        # Validate results (sanity check)
        if f_hz <= 0:
            logger.warning(f"Invalid frequency reading: {f_hz} Hz")
            return False, None, None

        if p_dbm < -200 or p_dbm > 50:  # Reasonable power range for most SA
            logger.warning(f"Power reading out of expected range: {p_dbm} dBm")
            # Still return the value but warn

        return True, f_mhz, p_dbm

    except ValueError as e:
        logger.error(f"Error converting marker values: {e}")
        return False, None, None
    except Exception:
        logger.exception("Unexpected error in read_max_peak")
        return False, None, None


if __name__ == "__main__":
    # Setup simple logging for console output
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Connect to the instrument with retry logic
    ip = '192.168.1.105'
    rm, sa_wrapper = SCPIWrapper.connect(
        ip=ip,
        log=logger,
        name='SA',
        max_retries=3,
        retry_delay=1.0,
        timeout_ms=10000
    )

    if sa_wrapper is None:
        sys.exit(1)

    # Get the underlying instrument for functions that need raw access
    sa = sa_wrapper.instr

    try:
        # Reset and clear all status (errors) of the spectrum analyzer
        sa_wrapper.write("*RST")
        sa_wrapper.write("*CLS")
        # Set the spectrum analyzer to maximal span
        sa_wrapper.write("sense:FREQuency:SPAN:FULL")
        # Set auto resolution bandwidth
        sa_wrapper.write("sense:BANDwidth:RESolution:AUTO ON")
        # Set the trace to write mode
        sa_wrapper.write(":TRACe1:TYPE WRITe")
        # Set the detector to positive peak
        sa_wrapper.write("sense:DETEctor POSitive")
        # Set the sweep mode to single sweep
        sa_wrapper.write("INITiate:CONTinuous OFF")
        # Start the sweep
        sa_wrapper.write("INITiate:IMMediate")
        # Wait for the sweep to complete
        sa.query("*OPC?")

        # Read the maximum peak (frequency and power) with error handling
        success, Fc, p = read_max_peak(sa)
        if not success:
            logger.error("Failed to find initial peak, exiting")
            sys.exit(1)

        # Set the reference level to the maximum
        max_level = np.ceil(p / 10 + 1) * 10
        sa_wrapper.write(f"DISP:WIND:TRAC:Y:RLEV {max_level}")

        # Set the span to 100 MHz, 10 MHz, 1 MHz, 100 kHz, 10 kHz, 1 kHz, 100 Hz
        Fspan = np.logspace(2, -4, 7)  # Span in MHz

        for span in Fspan:
            sa_wrapper.write(f"sense:FREQuency:CENTer {Fc} MHz")
            sa_wrapper.write(f"sense:FREQuency:SPAN {span} MHz")
            sa_wrapper.write("INITiate:IMMediate")
            # Wait for the sweep to complete
            sa.query("*OPC?")

            # Read the maximum peak with error handling
            success, Fc, p = read_max_peak(sa)
            if not success:
                logger.warning(f"Failed to find peak at span {span} MHz, skipping...")
                continue

            logger.info(f'Center Frequency: {Fc:.6f} MHz, Span: {span:.2e} MHz, Peak: {p:.2f} dBm')

        # Read the final RBW with error handling using the wrapper's enhanced query
        success, rbw = sa_wrapper.query("sense:BANDwidth:RESolution?", expected_type=float)
        if success:
            logger.info(f'Last RBW: {rbw:.2f} Hz')
        else:
            logger.warning("Failed to read final RBW")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")

    except Exception as e:
        logger.exception(f"Unexpected error during operation - {e}")

    finally:
        # Always close connections
        try:
            if sa is not None:
                sa.close()
            if rm is not None:
                rm.close()
            logger.info("Connections closed")
        except Exception as e:
            logger.exception(f"Error closing connections - {e}")
