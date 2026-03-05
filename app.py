from data_creaty.data_scr import Building_url
from data_creaty.data_ext import DataExtractor
from data_creaty.data_cleaning import data_cleaning
from model.model_train import train_predict

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

import joblib
import pandas as pd
import numpy as np
import re


import streamlit as st
import pandas as pd
import base64

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    logo_base64 = get_base64("app_logo.png")
    logo_html = f'data:image/png;base64,{logo_base64}'
except:
    logo_html = ""

# 🎨 Belirgin (Gözəçarpan) Dizayn üçün CSS
st.markdown(f"""
    <style>
    .main-header-container {{
        background-color: #EBF0F5; /* Daha tünd və doyğun boz-mavi */
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #CFD8E3; /* Daha qalın və görünən sərhəd */
        
        /* Güclü kölgə effekti */
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1); 
        
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        margin-bottom: 30px;
    
    }}
    
    .header-logo {{
        width: 90px;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.2));
    }}
    
    .header-text {{
        color: #0F172A; /* Tam tünd rəng */
        font-size: 36px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown(f"""
        <div class="main-header-container">
            <img src="{logo_html}" class="header-logo">
            <h1 class="header-text">Ev Qiyməti Təxmin Modeli</h1>
        </div>
    """, unsafe_allow_html=True)



with st.container():
    # HTML daxilində checkbox-ları yerləşdiririk
    st.markdown('<div class="options-container">', unsafe_allow_html=True)
    st.markdown('<p class="options-title" style="text-align: center;">⚙️ Model Seçimləri</p>', unsafe_allow_html=True)
    
    # Sütunlara bölmək olar ki, yan-yana görünsünlər
    mode = st.radio(
        "Xais edirik bir Mode secin:",
        ["Data Scraping", "Data Analiz", "Model Training", "House Predict"],
        horizontal=True # Yan-yana istəyirsənsə True et
    )


if mode=="Data Scraping":
    st.markdown("<h3 style='text-align: center;'>🌐 Məlumatların Toplanması (Scraping)</h3>", unsafe_allow_html=True)


    mode = st.radio("Scrap etmek istediyiniz mode secin:",
        ["Menziller", "Heyet evi / Bag evi"],
        horizontal=True )


    if mode == "Menziller":
        mode="menziller"

    else:
        mode="heyet-evleri"

    file_name_input = st.text_input("Yadda saxlanılacaq faylın adı:", value="builds_data")
    out_cvs = file_name_input 
       
    # Skrapinqi başlatmaq üçün bir düymə qoymaq məsləhətdir
    if st.button("Scraping-i Başlat"):    

        with st.spinner('Məlumatlar toplanılır, zəhmət olmasa gözləyin...'):
            try:
                # 1. URL-lərin toplanması
                output_file='Build_urls'
                my_bar = st.progress(0, text="Bina linkleri goturulur...")
                build_scr = Building_url(output_file=output_file,mode=mode)
                build_scr.start(start_room=1,end_room=1,progress_bar=my_bar)
                st.success("✅ URL-lər uğurla toplandı!")

                # 2. Məlumatların çıxarılması
                data_ex = DataExtractor(input_js='data/Build_urls.json', out_cvs=out_cvs)
                my_bar = st.progress(0, text="Bina melumatlari cixardilir...")
                data_ex.start_scr(progress_bar=my_bar)
                
                st.success(f"🎉 Bütün məlumatlar {output_file} faylına qeyd edildi!")
                
                # Nəticəni ekranda göstərək
                df_raw = pd.read_csv(out_cvs)
                st.dataframe(df_raw.head(8))
         
            except Exception as e:
                st.error(f"Xəta baş verdi: {e}")

    if st.button("Datani Temizle"):  
        
        df_raw = pd.read_csv(out_cvs)
        with st.spinner('Məlumatlar təmizlənir, zəhmət olmasa gözləyin...'):
            cleaner = data_cleaning(df_raw)
            df_cl = cleaner.full_data(out_csv=out_cvs)
            st.dataframe(df_cl.head(20))

            st.success("✅ Məlumatlar uğurla təmizləndi!")




elif mode == "Model Training":

    model_choice = st.sidebar.selectbox(
            "İstifadə ediləcək modeli seçin:",
            ["Linear Regression", "Decision Tree", "Random Forest", "SVR"]
            )
    
    st.markdown("<h3 style='text-align: center;'>Telim Datasi</h3>", unsafe_allow_html=True)

    param_method = st.sidebar.radio(
        "Parametr daxiletmə üsulu:",
        ["Avtomatik (Default)", "Hazır Siyahıdan Seç", "Əllə Daxil Et (Manual Dictionary)"]
    )

    params = {} # Modelə ötürüləcək əsas parametr lüğəti

    # --- 1. SEÇİM: Hazır Siyahıdan Seç (Sənin əvvəlki hazır inputların) ---
    if param_method == "Hazır Siyahıdan Seç":
    
        st.info(f"⚙️ {model_choice} üçün spesifik parametrlər:")
        col1, col2 = st.columns(2)
        
        if model_choice == "Random Forest":
            with col1:
                params['n_estimators'] = st.number_input("Ağac sayı (n_estimators):", min_value=10, max_value=100000, value=100)
            with col2:
                params['max_depth'] = st.number_input("Max Depth:", min_value=1, max_value=50, value=10)
                
        elif model_choice == "Decision Tree":
            with col1:
                params['max_depth'] = st.number_input("Max Depth:", min_value=1, max_value=100, value=5)
            with col2:
                params['criterion'] = st.selectbox("Criterion:", ["squared_error", "friedman_mse", "absolute_error"])
                
        elif model_choice == "SVR":
            with col1:
                params['kernel'] = st.selectbox("Kernel:", ["rbf", "linear", "poly"])
            with col2:
                params['C'] = st.slider("C (Regularization):", 0.1, 100.0, 1.0)
                
        elif model_choice == "Linear Regression":
            st.write("Bu model üçün xüsusi parametr tənzimləməsinə ehtiyac yoxdur.")





    elif param_method == "Əllə Daxil Et (Manual Dictionary)":
        # Parametrin adı (məsələn: n_estimators)
        param_name = st.sidebar.text_input("Parametr adı (məs: max_depth):")
        
        # Parametrin dəyəri (məsələn: 10)
        param_value = st.sidebar.text_input("Parametr dəyəri:")

        # Əlavə et düyməsi
        if st.sidebar.button("Parametri siyahıya əlavə et"):
            if param_name and param_value:
                # Dəyərin rəqəm olub-olmadığını yoxlayaq
                try:
                    # Əgər rəqəmdirsə rəqəmə çeviririk (int və ya float)
                    if "." in param_value:
                        val = float(param_value)
                    else:
                        val = int(param_value)
                except ValueError:
                    # Əgər rəqəm deyilsə olduğu kimi saxlayırıq (string)
                    val = param_value
                
                # Session State-də lüğəti saxlayırıq ki, səhifə yenilənəndə itməsin
                if 'custom_dict' not in st.session_state:
                    st.session_state.custom_dict = {}
                
                st.session_state.custom_dict[param_name] = val
                st.sidebar.success(f"Əlavə edildi: {param_name} = {val}")


    else:
        st.sidebar.info("Model ilkin (default) parametrlərlə işləyəcək.")
        params = {} # Boş qalır


    # 2. Dataframe-i vizual olaraq göstəririk
    out_cvs = st.text_input("Datanin adini verin:", value="builds_data")

    df_cl=pd.read_csv(out_cvs)
    st.dataframe(df_cl, use_container_width=True)



    if 'model_trained' not in st.session_state:
        st.session_state.model_trained = False

    if st.button("Təlimi Başlat"):
        try:
            # Modeli seçilən parametrlərlə yaradırıq (**params lüğəti bura ötürülür)
            if model_choice == "Linear Regression":
                model = LinearRegression(**params)
            elif model_choice == "Decision Tree":
                model = DecisionTreeRegressor(**params)
            elif model_choice == "Random Forest":
                model = RandomForestRegressor(**params)
            elif model_choice == "SVR":
                model = SVR(**params)

            with st.spinner(f'{model_choice} təlim edilir...'):
                # Sənin train_predict klasın
                train_model = train_predict(data=df_cl, target='price', model=model)
                train_model.train()
                
                st.session_state.train_model = train_model
                st.session_state.model_trained = True
                st.success(f"✅ {model_choice} modeli uğurla öyrədildi!")

        except TypeError as e:
            st.error(f"❌ Səhv parametr daxil edilib: {e}")
            st.info("İpucu: Parametr adının doğruluğunu model documantasiyasindan yoxlayın.")
        except Exception as e:
            st.error(f"💥 Xəta baş verdi: {e}")
        
        
        joblib.dump(train_model, 'model/save_model/trained_house_model.pkl')

        # 2. Öyrədilmiş obyekti və vəziyyəti session_state-də saxlayırıq
        st.session_state.train_model = train_model
        st.session_state.model_trained = True
        
        st.success(f"{model_choice} modeli uğurla öyrədildi!")

        # 3. Yalnız model öyrədildikdən sonra Predict düyməsini göstəririk
    if st.session_state.model_trained:
        st.divider()
        st.subheader("Proqnoz Mərhələsi")
        
        if st.button("Modeli Yüklə və Predict Et"):

            load_model=st.session_state.train_model
            predictions = load_model.predict_model()
            
            st.write("Yüklənmiş modeldən alınan nəticələr:")
            st.dataframe(predictions)

        metrics_mode = selected_metrics = st.multiselect("Hesablanacaq metrikaları seçin:",
            ["R2 Score", "Mean Absolute Error","Mean Squared Error","Root Mean Squared Error"],default=["R2 Score"])

        if st.button("Modelin scorelarina baxin "):

            load_model=st.session_state.train_model


            metrisc_li=load_model.metrics_score(mode=metrics_mode)

            for key,val in metrisc_li.items():
                st.write(f'Metrics: {key} - {val}')
            
        