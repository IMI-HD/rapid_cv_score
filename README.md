# RapidCVScore - Rapid Computation of Cardiovascular Risk Scores

_Philipp Goos, Sanketa Hegde, Merten Prüser, Erenik Krasniqi, Constanze Schmidt, Christoph Dieterich, ACRIBiS Study Group, Angela Merzweiler (2024):
RapidCVScore - Rapid Computation of Cardiovascular Risk Scores.
GMDS Jahrestagung 2024, 9/10/2024.
Available online at https://gesundheit-gemeinsam.de/gmds/ ._

## Risk scores

### CHA<sub>2</sub>DS<sub>2</sub>-VASc

Original publication: https://doi.org/10.1378/chest.09-1584
<br/>
Online calculator: https://www.chadsvasc.org/

### SMART

Original publication: https://doi.org/10.1136/heartjnl-2013-303640
<br/>
Computational formulas: https://heart.bmj.com/content/heartjnl/99/12/866.full.pdf?with-ds=yes#page=13

Recalibration: https://doi.org/10.1161/CIRCULATIONAHA.116.021314
<br/>
Recalibrated computational formulas: https://www.ahajournals.org/action/downloadSupplement?doi=10.1161%2FCIRCULATIONAHA.116.021314&file=021314_supplemental_material.pdf#page=16

Assumptions on the effects of antithrombotic treatment: https://doi.org/10.1016/S0140-6736(09)60503-1

Online calculator: https://u-prevent.com/calculators/smartScore

### MAGGIC

Original publication: https://doi.org/10.1093/eurheartj/ehs337
<br/>
Chart to calculate the integer risk score : https://academic.oup.com/view-large/figure/89301700/ehs33702.jpeg

Online calculator: http://www.heartfailurerisk.org/

## Installation

```Shell
# Clone repository
git clone git@github.com:IMI-HD/rapid_cv_score.git
cd rapid_cv_score

# Install packages
py -m pip install -r requirements.txt

# Run tests
py -m unittest discover test

# Run simple gui
py gui.py
```