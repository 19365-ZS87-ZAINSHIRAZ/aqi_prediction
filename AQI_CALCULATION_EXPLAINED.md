# AQI Calculation Explanation

## How AQI is Calculated (EPA Standard)

The system uses the **official EPA (Environmental Protection Agency)** method for calculating AQI.

### Formula

For each pollutant, AQI is calculated using linear interpolation:

```
AQI = ((AQI_high - AQI_low) / (C_high - C_low)) × (C - C_low) + AQI_low
```

Where:
- `C` = Pollutant concentration
- `C_low` = Breakpoint concentration ≤ C
- `C_high` = Breakpoint concentration ≥ C  
- `AQI_low` = AQI value corresponding to C_low
- `AQI_high` = AQI value corresponding to C_high

### PM2.5 Breakpoints (EPA Standard)

| PM2.5 (µg/m³) | AQI Range | Category |
|---------------|-----------|----------|
| 0.0 - 12.0 | 0 - 50 | Good |
| 12.1 - 35.4 | 51 - 100 | Moderate |
| 35.5 - 55.4 | 101 - 150 | Unhealthy for Sensitive Groups |
| 55.5 - 150.4 | 151 - 200 | Unhealthy |
| 150.5 - 250.4 | 201 - 300 | Very Unhealthy |
| 250.5 - 500.4 | 301 - 500 | Hazardous |

### Example: Why Islamabad Shows AQI 70

**Calculation:**
- **PM2.5 concentration:** 21 µg/m³
- **Breakpoint range:** 12.1 - 35.4 µg/m³ (Moderate)
- **AQI range:** 51 - 100

**Formula application:**
```
AQI = ((100 - 51) / (35.4 - 12.1)) × (21 - 12.1) + 51
AQI = (49 / 23.3) × 8.9 + 51
AQI = 2.103 × 8.9 + 51
AQI = 18.7 + 51
AQI = 69.7 ≈ 70
```

✅ **Result: AQI 70 (Moderate)**

This is **100% CORRECT** according to EPA standards!

## Multi-Pollutant AQI

When multiple pollutants are measured, the system:

1. Calculates individual AQI for each pollutant
2. Takes the **MAXIMUM** AQI value (dominant pollutant approach)
3. Reports that as the overall AQI

**Example:**
- PM2.5 → AQI 70
- PM10 → AQI 63
- NO2 → AQI 45
- **Overall AQI = 70** (PM2.5 is dominant)

## Why Different Sources Show Different Values?

### Reasons for AQI variations:

1. **Different monitoring stations**
   - US Embassy station vs. local government stations
   - Different locations in the city

2. **Different time periods**
   - Hourly vs. daily averages
   - Real-time vs. 24-hour average

3. **Different pollutant mixes**
   - Some sites measure more pollutants than others
   - Different dominant pollutants

4. **Calculation methods**
   - US EPA vs. local standards
   - Different averaging periods

### All calculations in this system:
✅ Use **official EPA breakpoints**
✅ Follow **EPA calculation formula**  
✅ Use **dominant pollutant** approach (standard method)
✅ Apply **linear interpolation** correctly

**The AQI values shown are scientifically accurate!** 🎯

---

**Last Updated:** May 3, 2026
**Standard:** US EPA AQI Calculation Method
