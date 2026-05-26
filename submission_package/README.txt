Περιεχόμενα πακέτου
===================

report/
- Report_gia_klimatismo.pdf: τελικό report για παράδοση.
- Report_gia_klimatismo.tex: πηγαίο αρχείο LaTeX του report.
- compile_report_a.sh: script για compile του report.
- floor_plan_G1.png: εικόνα κάτοψης που χρειάζεται το LaTeX αρχείο.

calculations/
- cooling_load_calculation.py: υπολογισμοί ψυκτικών φορτίων με CLTD/CLF.
- hvac_design_calculation.py: ψυχρομετρικοί/κλιματιστικοί υπολογισμοί συστήματος.
- psychrometric_chart.py: παραγωγή ψυχρομετρικών διαγραμμάτων.
- validate_ashrae_csv.py: έλεγχος/τεκμηρίωση των CSV πινάκων ASHRAE.
- Αποτελεσματα_CLTD_Ερωτημα_β.csv: παραγόμενα αποτελέσματα ερωτήματος β.
- Φυλλο_εργασιας_CLTD (1)(Table 1) (1).csv: αναλυτικό φύλλο εργασίας CLTD.
- ASHRAE_Tables/: πίνακες αναφοράς της μεθόδου ASHRAE σε CSV.

Σημείωση για τα ASHRAE CSV
==========================

Τα βασικά scripts υπολογισμών, δηλαδή τα cooling_load_calculation.py,
hvac_design_calculation.py και psychrometric_chart.py, δεν διαβάζουν απευθείας τα
CSV του φακέλου ASHRAE_Tables. Οι τιμές πινάκων που χρησιμοποιούνται στους
υπολογισμούς είναι ήδη περασμένες μέσα στον κώδικα.

Ο φάκελος ASHRAE_Tables περιλαμβάνεται για πληρότητα, τεκμηρίωση και έλεγχο των
πινάκων μέσω του validate_ashrae_csv.py. Άρα δεν είναι απαραίτητος για να τρέξουν
οι βασικοί υπολογισμοί, αλλά είναι σχετικός με την τεκμηρίωση της μεθοδολογίας.
