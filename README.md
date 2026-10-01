# Decopro

<img width="107" height="150" alt="decopro" src="https://github.com/user-attachments/assets/3ac5b3fb-96cc-48bb-971f-d0541244ec59" />

DecoPro is a software tool designed to simulate the progressive compaction of sedimentary successions through geological time in both onshore and offshore settings. The reconstruction begins with the deposition of the oldest stratigraphic unit and progresses forward in time as successively younger sedimentary units are added. As sediment accumulates, previously deposited units are progressively buried and compacted, resulting in a reduction in both their thickness and porosity.
Through this sequential reconstruction, DecoPro tracks changes in the thickness, burial depth, and porosity of each stratigraphic unit from the time of deposition to the present day.

DecoPro implements a porosity–depth relationship based on the classical exponential compaction law proposed by Athy (1930) and Hedberg (1936) and subsequently applied to basin analysis and backstripping by Sclater and Christie (1980). The software follows the methodology described by Allen and Allen (2013), assuming that porosity decreases exponentially with increasing burial depth. Lithology-dependent compaction parameters are used to calculate the progressive compaction of each stratigraphic unit as sedimentary loading increases through time.


References: 

[1] Allen, P. A., & Allen, J. R. (2013). Basin Analysis: Principles and Application to Petroleum Play Assessment (1st ed). John Wiley & Sons, Incorporated.

[2] Athy, L. F. (1930). Density, Porosity, and Compaction of Sedimentary Rocks. AAPG Bulletin, 14(1), 1–24. https://doi.org/10.1306/3D93289E-16B1-11D7-8645000102C1865D

[3] Hedberg, H. D. (1936). Gravitational compaction of clays and shales. 5, 31(184), 241–287.
Sclater, J. G., & Christie, P. A. F. (1980). Continental stretching: An explanation of the Post‐Mid‐Cretaceous subsidence of the central North Sea Basin. Journal of Geophysical Research: Solid Earth, 85(B7), 3711–3739. https://doi.org/10.1029/JB085iB07p03711


## Installation

### Windows

1. Execute build.bat

### Linux

1. Execute build.sh
