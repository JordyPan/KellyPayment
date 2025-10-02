import base64
import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fpdf import FPDF
import io

# Page configuration
st.set_page_config(
    page_title="Kelly Salary Calculator",
    page_icon="💰",
    layout="wide"
)


def set_background_image(uploaded_file=None):
    """Set a background image for the app with proper text readability"""
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode()
        background_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        """
    else:
        background_css = """
        <style>
        .stApp {
            background: #ffffff;
        }
        """

    common_css = """
    <style>
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.85);
        z-index: -1;
    }
    .main-header {
        background: linear-gradient(135deg, #1a5276, #2980b9);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Blue primary buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1a5276, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 15px 30px !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #154360, #21618c) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3) !important;
    }

    /* Blue secondary buttons */
    .stButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #3498db, #5dade2) !important;
        color: white !important;
        border: none !important;
    }

    .stButton>button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #2980b9, #3498db) !important;
    }

    /* Download button styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 15px 30px !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #229954, #27ae60) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
    """

    full_css = background_css + common_css
    st.markdown(full_css, unsafe_allow_html=True)


class SalaryPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Eastern Health - Salary Calculation Report', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_salary_pdf(calculation_data):
    pdf = SalaryPDF()
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'Fortnightly Salary Calculation Report', 0, 1, 'C')
    pdf.ln(10)

    # Basic Information
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Basic Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Hourly Rate: ${calculation_data["hourly_rate"]:.2f}', 0, 1)
    pdf.cell(0, 8, f'Standard Fortnight Hours: {calculation_data["standard_hours"]}', 0, 1)
    pdf.cell(0, 8, f'Pay Period: {calculation_data["start_date"]} to {calculation_data["end_date"]}', 0, 1)
    pdf.ln(5)

    # Hours Worked
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Hours Worked', 0, 1)
    pdf.set_font('Arial', '', 12)

    hours_data = [
        ('Standard Hours', calculation_data['ordinary_hours'], calculation_data['ordinary_pay']),
        ('Overtime @1.5', calculation_data['overtime_15_hours'], calculation_data['overtime_15_pay']),
        ('Overtime @2.0', calculation_data['overtime_20_hours'], calculation_data['overtime_20_pay']),
        ('Weekend Hours', calculation_data['weekend_hours'], calculation_data['weekend_pay']),
        ('Public Holiday Hours', calculation_data['public_holiday_hours'], calculation_data['public_holiday_pay']),
        ('Unrostered OT', calculation_data['unrostered_ot_hours'], calculation_data['unrostered_ot_pay']),
        ('On Call Hours', calculation_data['on_call_hours'], calculation_data['on_call_pay']),
    ]

    for category, hours, amount in hours_data:
        if hours > 0:
            pdf.cell(0, 8, f'{category}: {hours}h = ${amount:,.2f}', 0, 1)

    pdf.ln(5)

    # Allowances
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Allowances', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Uniform Allowance: ${calculation_data["uniform_allowance"]:.2f}', 0, 1)
    pdf.cell(0, 8, f'Medical Education Allowance: ${calculation_data["education_allowance"]:.2f}', 0, 1)
    if calculation_data['meal_allowances'] > 0:
        pdf.cell(0, 8,
                 f'Meal Allowances ({calculation_data["meal_allowances"]}): ${calculation_data["meal_allowance_pay"]:.2f}',
                 0, 1)
    pdf.ln(5)

    # Earnings Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. Earnings Summary', 0, 1)
    pdf.set_font('Arial', '', 12)

    earnings_data = [
        ('Ordinary Hours', calculation_data['ordinary_pay']),
        ('Overtime @1.5', calculation_data['overtime_15_pay']),
        ('Overtime @2.0', calculation_data['overtime_20_pay']),
        ('Weekend Hours', calculation_data['weekend_pay']),
        ('Public Holiday Hours', calculation_data['public_holiday_pay']),
        ('Unrostered OT', calculation_data['unrostered_ot_pay']),
        ('On Call', calculation_data['on_call_pay']),
        ('Allowances', calculation_data['total_allowances']),
    ]

    for category, amount in earnings_data:
        if amount > 0:
            pdf.cell(0, 8, f'{category}: ${amount:,.2f}', 0, 1)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'Total Gross: ${calculation_data["total_payments"]:,.2f}', 0, 1)
    pdf.ln(5)

    # Deductions
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5. Deductions', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Income Tax: ${calculation_data["income_tax"]:,.2f}', 0, 1)
    pdf.cell(0, 8, f'Car Park: ${calculation_data["car_park"]:.2f}', 0, 1)
    pdf.cell(0, 8, f'Salary Packaging: ${calculation_data["salary_packaging"]:.2f}', 0, 1)
    pdf.cell(0, 8, f'Superannuation ({calculation_data["super_rate"]}%): ${calculation_data["superannuation"]:,.2f}', 0,
             1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'Total Deductions: ${calculation_data["total_deductions"]:,.2f}', 0, 1)
    pdf.ln(5)

    # Final Summary
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '6. Final Summary', 0, 1)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'NET PAY: ${calculation_data["net_pay"]:,.2f}', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Total Hours: {calculation_data["total_hours"]}', 0, 1)
    pdf.cell(0, 8, f'Effective Hourly Rate: ${calculation_data["effective_hourly_rate"]:.2f}', 0, 1)

    return pdf


def calculate_income_tax(income):
    """Calculate income tax based on Australian tax brackets for 2025-26"""
    annual_income = income * 26
    tax = 0

    if annual_income <= 18200:
        tax = 0
    elif annual_income <= 45000:
        tax = (annual_income - 18200) * 0.16
    elif annual_income <= 135000:
        tax = (45000 - 18200) * 0.16 + (annual_income - 45000) * 0.30
    elif annual_income <= 190000:
        tax = (45000 - 18200) * 0.16 + (135000 - 45000) * 0.30 + (annual_income - 135000) * 0.37
    else:
        tax = (45000 - 18200) * 0.16 + (135000 - 45000) * 0.30 + (190000 - 135000) * 0.37 + (
                    annual_income - 190000) * 0.45

    return tax / 26


def display_calculation_results():
    """Display the calculation results from session state"""
    if 'calculation_data' not in st.session_state:
        return

    calculation_data = st.session_state.calculation_data

    st.markdown("---")
    st.subheader("📊 Pay Calculation Results")

    # Display results
    col1, col2 = st.columns(2)

    with col1:
        st.write("**EARNINGS**")
        st.write(f"Ordinary Hours ({calculation_data['ordinary_hours']}h): ${calculation_data['ordinary_pay']:,.2f}")

        if calculation_data.get('standard_overtime_15_hours', 0) > 0:
            st.write(
                f"Standard OT 1.5x ({calculation_data['standard_overtime_15_hours']}h): ${calculation_data['standard_ot_15_pay']:,.2f}")

        if calculation_data.get('standard_overtime_20_hours', 0) > 0:
            st.write(
                f"Standard OT 2.0x ({calculation_data['standard_overtime_20_hours']}h): ${calculation_data['standard_ot_20_pay']:,.2f}")

        if calculation_data['overtime_15_hours'] > 0:
            st.write(
                f"Overtime @1.5 ({calculation_data['overtime_15_hours']}h): ${calculation_data['overtime_15_pay']:,.2f}")

        if calculation_data['overtime_20_hours'] > 0:
            st.write(
                f"Overtime @2.0 ({calculation_data['overtime_20_hours']}h): ${calculation_data['overtime_20_pay']:,.2f}")

        if calculation_data['unrostered_ot_hours'] > 0:
            st.write(
                f"Unrostered OT 2.0x ({calculation_data['unrostered_ot_hours']}h): ${calculation_data['unrostered_ot_pay']:,.2f}")

        if calculation_data['on_call_hours'] > 0:
            st.write(f"On Call PSG-N/S ({calculation_data['on_call_hours']}h): ${calculation_data['on_call_pay']:,.2f}")

        if calculation_data['weekend_hours'] > 0:
            st.write(f"Weekend 1.5x ({calculation_data['weekend_hours']}h): ${calculation_data['weekend_pay']:,.2f}")

        if calculation_data['public_holiday_hours'] > 0:
            st.write(
                f"Public Holiday 2.5x ({calculation_data['public_holiday_hours']}h): ${calculation_data['public_holiday_pay']:,.2f}")

        st.write("**ALLOWANCES**")
        st.write(f"Uniform Allowance: ${calculation_data['uniform_allowance']:,.2f}")
        st.write(f"Continuing Medical Education Allowance: ${calculation_data['education_allowance']:,.2f}")

        if calculation_data['meal_allowances'] > 0:
            st.write(
                f"Meal Allowances ({calculation_data['meal_allowances']}): ${calculation_data['meal_allowance_pay']:,.2f}")

        st.write(f"**TOTAL GROSS: ${calculation_data['total_payments']:,.2f}**")

    with col2:
        st.write("**DEDUCTIONS**")
        st.write(f"Income Tax: ${calculation_data['income_tax']:,.2f}")
        st.write(f"Car Park: ${calculation_data['car_park']:,.2f}")
        st.write(f"Salary Packaging: ${calculation_data['salary_packaging']:,.2f}")
        st.write(f"**TOTAL DEDUCTIONS: ${calculation_data['total_deductions']:,.2f}**")
        st.write("")
        st.write(f"**NET PAY: ${calculation_data['net_pay']:,.2f}**")
        st.write(f"Superannuation ({calculation_data['super_rate']}%): ${calculation_data['superannuation']:,.2f}")

    # Hours summary table
    st.subheader("Hours Summary")

    hours_data = {
        'Category': [
            'Standard Hours (Ordinary Rate)',
            'Standard OT (1.5x Rate)',
            'Standard OT (2.0x Rate)',
            'Overtime @1.5 (1.5x Rate)',
            'Overtime @2.0 (2.0x Rate)',
            'Unrostered OT (2.0x Rate)',
            'On Call PSG-N/S (Special Rate)',
            'Weekend Hours (1.5x Rate)',
            'Public Holiday Hours (2.5x Rate)',
            'TOTAL HOURS'
        ],
        'Hours': [
            calculation_data['ordinary_hours'],
            calculation_data.get('standard_overtime_15_hours', 0),
            calculation_data.get('standard_overtime_20_hours', 0),
            calculation_data['overtime_15_hours'],
            calculation_data['overtime_20_hours'],
            calculation_data['unrostered_ot_hours'],
            calculation_data['on_call_hours'],
            calculation_data['weekend_hours'],
            calculation_data['public_holiday_hours'],
            calculation_data['total_hours']
        ],
        'Amount': [
            calculation_data['ordinary_pay'],
            calculation_data.get('standard_ot_15_pay', 0),
            calculation_data.get('standard_ot_20_pay', 0),
            calculation_data['overtime_15_pay'],
            calculation_data['overtime_20_pay'],
            calculation_data['unrostered_ot_pay'],
            calculation_data['on_call_pay'],
            calculation_data['weekend_pay'],
            calculation_data['public_holiday_pay'],
            calculation_data['total_payments'] - calculation_data['total_allowances']
        ]
    }

    hours_df = pd.DataFrame(hours_data)
    st.dataframe(hours_df, use_container_width=True, hide_index=True)

    # Generate PDF Report section
    st.markdown("---")
    st.subheader("📄 Generate Report")

    # Generate PDF button
    if st.button("📄 Generate PDF Report", type="secondary", use_container_width=True, key="generate_pdf"):
        try:
            # Generate PDF
            pdf = create_salary_pdf(calculation_data)

            # Create PDF bytes
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            # Store in session state
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_generated = True
            st.success("✅ PDF report generated successfully!")

        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")

    # Download button (only show if PDF is generated)
    if st.session_state.get('pdf_generated', False) and st.session_state.get('pdf_bytes'):
        st.download_button(
            label="📥 Download Salary Report PDF",
            data=st.session_state.pdf_bytes,
            file_name=f"salary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf"
        )


def calculate_pay(total_standard_hours, overtime_15_hours, overtime_20_hours,
                  total_weekend_hours, total_public_holiday_hours,
                  unrostered_overtime_hours, on_call_hours, on_call_rate,
                  hourly_rate, standard_hours,
                  uniform_allowance, education_allowance, meal_allowances, meal_rate,
                  car_park, salary_packaging, super_rate,
                  start_date, end_date):
    # Apply overtime rules to standard hours
    if total_standard_hours <= standard_hours:
        ordinary_hours = total_standard_hours
        standard_overtime_15_hours = 0
        standard_overtime_20_hours = 0
    else:
        overtime_hours = total_standard_hours - standard_hours
        standard_overtime_15_hours = min(2, overtime_hours)
        standard_overtime_20_hours = max(0, overtime_hours - 2)
        ordinary_hours = standard_hours

    # Calculate payments for each category
    ordinary_pay = ordinary_hours * hourly_rate
    standard_ot_15_pay = standard_overtime_15_hours * hourly_rate * 1.5
    standard_ot_20_pay = standard_overtime_20_hours * hourly_rate * 2.0
    overtime_15_pay = overtime_15_hours * hourly_rate * 1.5
    overtime_20_pay = overtime_20_hours * hourly_rate * 2.0
    unrostered_ot_pay = unrostered_overtime_hours * hourly_rate * 2.0
    on_call_pay = on_call_hours * on_call_rate
    weekend_pay = total_weekend_hours * hourly_rate * 1.5
    public_holiday_pay = total_public_holiday_hours * hourly_rate * 2.5

    # Calculate allowances
    meal_allowance_pay = meal_allowances * meal_rate
    total_allowances = uniform_allowance + education_allowance + meal_allowance_pay

    # Total payments
    total_payments = (ordinary_pay + standard_ot_15_pay + standard_ot_20_pay +
                      overtime_15_pay + overtime_20_pay + unrostered_ot_pay +
                      on_call_pay + weekend_pay + public_holiday_pay + total_allowances)

    # Calculate deductions
    taxable_income = total_payments

    base_tax = calculate_income_tax(taxable_income)
    medicare_levy = taxable_income * 0.02  # Always include Medicare for now
    income_tax = base_tax + medicare_levy

    superannuation = total_payments * (super_rate / 100)
    total_deductions = income_tax + car_park + salary_packaging
    net_pay = total_payments - total_deductions

    # Total hours
    total_hours = (ordinary_hours + standard_overtime_15_hours + standard_overtime_20_hours +
                   overtime_15_hours + overtime_20_hours + unrostered_overtime_hours +
                   on_call_hours + total_weekend_hours + total_public_holiday_hours)

    # Store all calculation data in session state
    st.session_state.calculation_data = {
        "hourly_rate": hourly_rate,
        "standard_hours": standard_hours,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "ordinary_hours": ordinary_hours,
        "ordinary_pay": ordinary_pay,
        "standard_overtime_15_hours": standard_overtime_15_hours,
        "standard_ot_15_pay": standard_ot_15_pay,
        "standard_overtime_20_hours": standard_overtime_20_hours,
        "standard_ot_20_pay": standard_ot_20_pay,
        "overtime_15_hours": overtime_15_hours,
        "overtime_15_pay": overtime_15_pay,
        "overtime_20_hours": overtime_20_hours,
        "overtime_20_pay": overtime_20_pay,
        "weekend_hours": total_weekend_hours,
        "weekend_pay": weekend_pay,
        "public_holiday_hours": total_public_holiday_hours,
        "public_holiday_pay": public_holiday_pay,
        "unrostered_ot_hours": unrostered_overtime_hours,
        "unrostered_ot_pay": unrostered_ot_pay,
        "on_call_hours": on_call_hours,
        "on_call_pay": on_call_pay,
        "uniform_allowance": uniform_allowance,
        "education_allowance": education_allowance,
        "meal_allowances": meal_allowances,
        "meal_allowance_pay": meal_allowance_pay,
        "total_allowances": total_allowances,
        "total_payments": total_payments,
        "income_tax": income_tax,
        "car_park": car_park,
        "salary_packaging": salary_packaging,
        "super_rate": super_rate,
        "superannuation": superannuation,
        "total_deductions": total_deductions,
        "net_pay": net_pay,
        "total_hours": total_hours,
        "effective_hourly_rate": net_pay / total_hours if total_hours > 0 else 0
    }

    st.session_state.calculation_complete = True


def main():
    # Initialize session state
    if 'calculation_complete' not in st.session_state:
        st.session_state.calculation_complete = False
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False
    if 'calculation_data' not in st.session_state:
        st.session_state.calculation_data = None
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = None

    # Background customization
    with st.sidebar:
        st.header("🎨 Customize Background")
        uploaded_file = st.file_uploader(
            "Upload your own background image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a custom background image for the app"
        )

    set_background_image(uploaded_file)

    if uploaded_file is not None:
        st.sidebar.success("✅ Custom background applied!")
    else:
        st.sidebar.info("📁 Upload an image for custom background")

    # Main header
    st.markdown(
        """
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5em;">💰 Salary Calculator</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.3em; opacity: 0.95;">Fortnightly Pay Calculator • HM12 Year 2 • Personalised for One and only Kelly Zhu Copyright©</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Only show input form if no calculation is complete
    if not st.session_state.calculation_complete:
        # Basic information
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Basic Information")
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=45.85395, step=0.01,
                                          key="hourly_rate")
            standard_fortnight_hours = st.number_input("Standard Fortnight Hours", min_value=0, value=76, step=1,
                                                       key="standard_hours")

        with col2:
            st.subheader("Pay Period")
            start_date = st.date_input("Pay Period Start Date", value=datetime(2025, 9, 15), key="start_date")
            end_date = st.date_input("Pay Period End Date", value=datetime(2025, 9, 28), key="end_date")

        st.markdown("---")

        # Hours worked
        st.subheader("🏥 Hours Worked This Fortnight")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write("**Standard Hours**")
            st.info("Regular weekday hours (Mon-Fri)")
            total_standard_hours = st.number_input(
                "Total Standard Hours",
                min_value=0.0,
                max_value=168.0,
                value=76.0,
                step=0.5,
                help="Your contracted 76 hours",
                key="standard_hours_input"
            )

        with col2:
            st.write("**Overtime @1.5**")
            st.info("Overtime hours paid at 1.5x rate")
            overtime_15_hours = st.number_input(
                "Overtime @1.5 Hours",
                min_value=0.0,
                max_value=168.0,
                value=2.0,
                step=0.5,
                help="Overtime hours paid at 1.5 times normal rate",
                key="ot_15"
            )

        with col3:
            st.write("**Overtime @2.0**")
            st.info("Overtime hours paid at 2.0x rate")
            overtime_20_hours = st.number_input(
                "Overtime @2.0 Hours",
                min_value=0.0,
                max_value=168.0,
                value=12.0,
                step=0.5,
                help="Overtime hours paid at 2.0 times normal rate",
                key="ot_20"
            )

        with col4:
            st.write("**Weekend Hours**")
            st.info("Hours worked on Saturday/Sunday")
            total_weekend_hours = st.number_input(
                "Total Weekend Hours",
                min_value=0.0,
                max_value=168.0,
                value=0.0,
                step=0.5,
                help="All weekend hours paid at 1.5x rate",
                key="weekend"
            )

        # Additional hours
        st.subheader("🕒 Additional Hours")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Public Holiday Hours**")
            st.info("Hours worked on public holidays")
            total_public_holiday_hours = st.number_input(
                "Total Public Holiday Hours",
                min_value=0.0,
                max_value=168.0,
                value=0.0,
                step=0.5,
                help="All public holiday hours paid at 2.5x rate",
                key="ph"
            )

        with col2:
            st.write("**Unrostered Overtime**")
            st.info("Additional overtime claimed by you")
            unrostered_overtime_hours = st.number_input(
                "Unrostered Overtime Hours",
                min_value=0.0,
                max_value=168.0,
                value=0.0,
                step=0.5,
                help="Unrostered OT claimed by you at 2.0x rate",
                key="unrostered"
            )

        with col3:
            st.write("**On Call (PSG-N/S)**")
            st.info("On call hours at special rate")
            on_call_hours = st.number_input(
                "On Call Hours",
                min_value=0.0,
                max_value=168.0,
                value=0.0,
                step=0.5,
                help="On call hours paid at $43.56000 per hour",
                key="on_call"
            )
            on_call_rate = st.number_input(
                "On Call Rate ($/hour)",
                min_value=0.0,
                value=43.56000,
                step=0.01,
                help="Special rate for on call hours",
                key="on_call_rate"
            )

        # Total hours
        total_hours = (total_standard_hours + overtime_15_hours + overtime_20_hours +
                       total_weekend_hours + total_public_holiday_hours +
                       unrostered_overtime_hours + on_call_hours)
        st.write(f"**Total Hours This Fortnight: {total_hours}**")

        st.markdown("---")

        # Allowances and deductions
        st.subheader("Allowances & Deductions")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Allowances**")
            uniform_allowance = st.number_input("Uniform Allowance", min_value=0.0, value=19.74, step=0.01,
                                                key="uniform")
            education_allowance = st.number_input("Medical Education Allowance", min_value=0.0, value=181.8, step=0.01,
                                                  key="education")
            meal_allowances = st.number_input("Number of Meal Allowances", min_value=0, value=2, step=1,
                                              key="meal_count")
            meal_rate = st.number_input("Meal Allowance Rate", min_value=0.0, value=11.13, step=0.01, key="meal_rate")

        with col2:
            st.write("**Deductions**")
            car_park = st.number_input("Car Park Deduction", min_value=0.0, value=86.30, step=0.01, key="car_park")
            salary_packaging = st.number_input("Salary Packaging", min_value=0.0, value=365.60, step=0.01,
                                               key="salary_pack")
            super_rate = st.number_input("Superannuation Rate (%)", min_value=0.0, max_value=20.0, value=12.0, step=0.1,
                                         key="super")

        # Calculate pay button
        if st.button("Calculate Fortnightly Pay", type="primary", use_container_width=True, key="calculate_pay"):
            calculate_pay(
                total_standard_hours, overtime_15_hours, overtime_20_hours,
                total_weekend_hours, total_public_holiday_hours,
                unrostered_overtime_hours, on_call_hours, on_call_rate,
                hourly_rate, standard_fortnight_hours,
                uniform_allowance, education_allowance, meal_allowances, meal_rate,
                car_park, salary_packaging, super_rate,
                start_date, end_date
            )
            st.rerun()

    # Display results if calculation is complete
    if st.session_state.calculation_complete:
        display_calculation_results()

        # Add a button to start over
        if st.button("🔄 Start New Calculation", type="primary", use_container_width=True, key="new_calc"):
            st.session_state.calculation_complete = False
            st.session_state.pdf_generated = False
            st.session_state.calculation_data = None
            st.session_state.pdf_bytes = None
            st.rerun()


if __name__ == "__main__":
    main()