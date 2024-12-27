from Logger import Logger
import math
logger = Logger()


class CalculatedValues:
    def __init__(self, calculated_values: list, car_proprties: dict):
        self.calculated_values = calculated_values
        self.car_proprties = car_proprties
        #This is typically assumed to be 14.7:1 for gasoline engines (stoichiometric ratio). 
        self.AFR = 14.7
        # The density of gasoline is roughly 0.74 kg/L.
        self.FUEL_DENSITY = 0.74


    def calculate_values(self, maf, speed, rpm):
        # Ensure that inputs are in the correct data type
        try:
            maf = float(maf)
            speed = float(speed)
            rpm = float(rpm)
        except ValueError:
            logger.error("All inputs (maf, speed, rpm) must be numbers.")
            return None
        
        # return a dictionary with the calculated values in the calculated_values list in a dynamic way
        return {
            key: func(maf, speed, rpm)
            for key, func in self.calculated_values.items()
        }
    

    def fuel_consumption_instant(self, maf):
        # Ensure that inputs are in the correct data type
        try:
            maf = float(maf)
        except ValueError:
            logger.error("All inputs (maf) must be numbers.")
            return None
        # Calculate fuel flow in L/hr
        fuel_flow = (maf / self.AFR / self.FUEL_DENSITY) * 3600
        return fuel_flow

    def fuel_consumption_l_100km(self, maf, speed):
        # Ensure that inputs are in the correct data type
        try:
            maf = float(maf)
            speed = float(speed)
        except ValueError:
            logger.error("All inputs (maf, speed) must be numbers.")
            return None
        # Calculate fuel flow in L/hr
        fuel_flow = (maf / self.AFR / self.FUEL_DENSITY) * 3600  # MAF is in grams per second
        # Avoid division by zero in case speed is zero
        if speed == 0:
            return fuel_flow
        # Calculate fuel consumption in L/100 km
        fuel_consumption = (fuel_flow * 100) / speed
        return fuel_consumption

    def estimate_gear(self, speed, rpm):
        # Ensure that inputs are in the correct data type
        try:
            speed = float(speed)
            rpm = float(rpm)
            tire_radius = float(self.car_proprties["tire_radius"])
            gear_ratios = self.car_proprties["gear_ratios"]
        except ValueError:
            logger.error("All inputs (speed, rpm, tire_radius, gear_ratios) must be numbers.")
            return None

        # Convert speed from km/h to m/s
        speed_m_s = speed * (1000.0 / 3600.0)

        # Avoid division by zero in case speed is zero
        if speed_m_s == 0:
            return 0

        # Calculate the gear ratio
        gear_ratio = (rpm * tire_radius * 2.0 * math.pi) / (speed_m_s * 60.0)

        # Find the closest matching gear ratio from known gear ratios
        closest_gear = min(gear_ratios, key=lambda x: abs(x - gear_ratio))

        return gear_ratios.index(closest_gear) + 1  # Return the gear number