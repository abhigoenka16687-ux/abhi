import streamlit as pd
import streamlit as st
import datetime

# Page configuration
st.set_page_config(
    page_title="Goods Dispatch Coordinator",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Goods Dispatch Coordination Portal")
st.markdown("Track and execute the dispatch workflow seamlessly across teams.")
st.write("---")

# Initialize session state to store orders if not already present
if 'orders' not in st.session_state:
    st.session_state.orders = {}

# -----------------------------------------------------------------------------
# SIDEBAR: Quick Stats & Navigation Help
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Activity Summary")
    total_orders = len(st.session_state.orders)
    st.metric(label="Total Orders Logged", value=total_orders)
    
    st.markdown("""
    ### Workflow Steps:
    1. **Sales Receipt** (Log incoming order)
    2. **Delivery Order** (Generate DO details)
    3. **Tally Invoice** (Mark accounting status)
    4. **Godown Dispatch** (Prepare WhatsApp share)
    """)

# -----------------------------------------------------------------------------
# MAIN INTERFACE: Step-by-Step Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 1. Receive Sales Order", 
    "📄 2. Create Delivery Order", 
    "📊 3. Tally Invoice Status", 
    "🚛 4. WhatsApp to Godown",
    "📋 Dispatch Dashboard"
])

# -----------------------------------------------------------------------------
# TAB 1: RECEIVE ORDER FROM SALES TEAM
# -----------------------------------------------------------------------------
with tab1:
    st.header("Step 1: Record Incoming Sales Order")
    
    with st.form("sales_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            order_id = st.text_input("Sales Order / Booking Reference No.*")
            client_name = st.text_input("Client / Party Name*")
        with col2:
            order_date = st.date_input("Order Date", datetime.date.today())
            sales_person = st.text_input("Sales Representative")
            
        st.markdown("### Item Details")
        item_details = st.text_area("Specify Items, Quantities, and Paper Specifications (e.g., Maplitho 60GSM, 50 Bundles)")
        
        submit_order = st.form_submit_button("Log Order & Move to DO")
        
        if submit_order:
            if not order_id or not client_name:
                st.error("Please fill out the Order Reference Number and Client Name.")
            else:
                st.session_state.orders[order_id] = {
                    "client_name": client_name,
                    "order_date": order_date.strftime("%Y-%m-%d"),
                    "sales_person": sales_person,
                    "item_details": item_details,
                    "do_created": False,
                    "do_number": "",
                    "vehicle_no": "",
                    "tally_status": "Pending",
                    "tally_inv_no": "",
                    "whatsapp_sent": False
                }
                st.success(f"Order {order_id} successfully logged! Proceed to Step 2.")

# -----------------------------------------------------------------------------
# TAB 2: MAKE A DELIVERY ORDER (DO)
# -----------------------------------------------------------------------------
with tab2:
    st.header("Step 2: Generate Delivery Order (DO)")
    
    pending_do = [k for k, v in st.session_state.orders.items() if not v["do_created"]]
    
    if not pending_do:
        st.info("No orders pending Delivery Order creation.")
    else:
        selected_order_do = st.selectbox("Select Order to Create DO:", pending_do, key="sb_do")
        order_info = st.session_state.orders[selected_order_do]
        
        # Display details from Step 1
        st.info(f"**Party:** {order_info['client_name']} | **Items:** {order_info['item_details']}")
        
        with st.form("do_form"):
            col1, col2 = st.columns(2)
            with col1:
                do_number = st.text_input("Generated DO Number*", value=f"DO-{selected_order_do}")
            with col2:
                vehicle_no = st.text_input("Assigned Vehicle / Transport Number (e.g., BR-01-XXXX)")
                
            submit_do = st.form_submit_button("Save Delivery Order")
            
            if submit_do:
                if not do_number:
                    st.error("Please enter a valid DO Number.")
                else:
                    st.session_state.orders[selected_order_do]["do_created"] = True
                    st.session_state.orders[selected_order_do]["do_number"] = do_number
                    st.session_state.orders[selected_order_do]["vehicle_no"] = vehicle_no
                    st.success(f"Delivery Order {do_number} saved. Ready for Tally Invoicing.")
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: MAKE INVOICE IN TALLY
# -----------------------------------------------------------------------------
with tab3:
    st.header("Step 3: Tally Accounting System Check")
    st.caption("Open your Tally ERP/Prime software, generate the official invoice, and record the reference below.")
    
    pending_tally = [k for k, v in st.session_state.orders.items() if v["do_created"] and v["tally_status"] == "Pending"]
    
    if not pending_tally:
        st.info("No orders currently waiting for Tally Invoice verification.")
    else:
        selected_order_tally = st.selectbox("Select Order for Tally Verification:", pending_tally, key="sb_tally")
        order_info = st.session_state.orders[selected_order_tally]
        
        st.markdown(f"""
        * **Client:** {order_info['client_name']}
        * **DO Number:** {order_info['do_number']}
        * **Items:** {order_info['item_details']}
        """)
        
        with st.form("tally_form"):
            tally_inv_no = st.text_input("Enter Tally Invoice Number*")
            confirm_tally = st.checkbox("I confirm that this invoice has been successfully entered and saved in Tally.")
            
            submit_tally = st.form_submit_button("Update Invoice Status")
            
            if submit_tally:
                if not tally_inv_no or not confirm_tally:
                    st.error("Please provide the Tally Invoice Number and check the confirmation box.")
                else:
                    st.session_state.orders[selected_order_tally]["tally_status"] = "Invoiced"
                    st.session_state.orders[selected_order_tally]["tally_inv_no"] = tally_inv_no
                    st.success(f"Invoice {tally_inv_no} linked. Proceed to notify Godown.")
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 4: SEND TO GODOWN VIA WHATSAPP
# -----------------------------------------------------------------------------
with tab4:
    st.header("Step 4: Dispatch Notification to Godown")
    
    pending_whatsapp = [k for k, v in st.session_state.orders.items() if v["tally_status"] == "Invoiced" and not v["whatsapp_sent"]]
    
    if not pending_whatsapp:
        st.info("No orders are currently cleared and waiting for Godown notification.")
    else:
        selected_order_wa = st.selectbox("Select Order to Dispatch to Godown:", pending_whatsapp, key="sb_wa")
        order_info = st.session_state.orders[selected_order_wa]
        
        # Structure the message explicitly for your warehouse operators
        whatsapp_message = (
            f"🚨 *NEW DISPATCH ORDER* 🚨\n\n"
            f"*DO Number:* {order_info['do_number']}\n"
            f"*Tally Inv No:* {order_info['tally_inv_no']}\n"
            f"*Party:* {order_info['client_name']}\n"
            f"*Vehicle No:* {order_info['vehicle_no'] if order_info['vehicle_no'] else 'Self-Arranged/Pending'}\n\n"
            f"*Items to Load:*\n{order_info['item_details']}\n\n"
            f"Please verify loading, sign the copy, and release the vehicle."
        )
        
        st.markdown("### Preview Text for WhatsApp")
        st.code(whatsapp_message, language="markdown")
        
        # WhatsApp Web click formulation
        # Replace with your actual Godown supervisor's phone number (include country code, no symbols)
        godown_phone = st.text_input("Godown Mobile Number (With country code, e.g., 919876543210)", value="91")
        
        # Format for WhatsApp API URL URL-safe strings
        import urllib.parse
        encoded_message = urllib.parse.quote(whatsapp_message)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={godown_phone}&text={encoded_message}"
        
        st.markdown(f'[🔗 Click Here to Send Message via WhatsApp]({whatsapp_url})')
        
        st.write("---")
        if st.button("Mark as Successfully Dispatched & Sent"):
            st.session_state.orders[selected_order_wa]["whatsapp_sent"] = True
            st.success("Order status updated to Complete!")
            st.rerun()

# -----------------------------------------------------------------------------
# TAB 5: DISPATCH DASHBOARD (LIVE OVERVIEW)
# -----------------------------------------------------------------------------
with tab5:
    st.header("Live Operational Pipeline")
    
    if not st.session_state.orders:
        st.warning("No operational logs recorded yet today.")
    else:
        # Convert dictionary to DataFrame for crisp tabular formatting
        df_display = []
        for key, val in st.session_state.orders.items():
            # Quick status logic badge representation
            status_step = "📥 Sales Logged"
            if val["do_created"]: status_step = "📄 DO Created"
            if val["tally_status"] == "Invoiced": status_step = "📊 Tally Ready"
            if val["whatsapp_sent"]: status_step = "✅ Sent to Godown"
            
            df_display.append({
                "Order Ref": key,
                "Party Name": val["client_name"],
                "Date": val["order_date"],
                "Current Stage": status_step,
                "DO Reference": val["do_number"],
                "Tally Inv": val["tally_inv_no"],
                "Vehicle": val["vehicle_no"]
            })
            
        st.dataframe(df_display, use_container_width=True)
