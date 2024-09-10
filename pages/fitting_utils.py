import numpy as np
import scipy.optimize as optimize
import matplotlib
matplotlib.use('Agg') 
from matplotlib import pyplot as plt
from scipy.integrate import odeint
import emcee
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from dash import html
import dash_bootstrap_components as dbc
from . import utils
import base64
from io import BytesIO

def restructure_metadata_fitting(df_metadata):
    species_selected = df_metadata["species"].unique()
    carbon_source_selected = df_metadata["carbon_source"].unique()
    concentrations_present = []
    lg_replicates = []
    fitting_comments = []
    for i in range(len(species_selected)):
        species_filtered_metadata = df_metadata[df_metadata["species"] == species_selected[i]]
        cur_species_concs = []
        cur_sp_lg_replicates = []
        cur_sp_comments = []
        for j in range(len(carbon_source_selected)):
            cs_filtered_metadata = species_filtered_metadata[species_filtered_metadata["carbon_source"] == carbon_source_selected[j]]
            unique_cs_concs = cs_filtered_metadata["cs_conc"].unique()
            unique_cs_concs = unique_cs_concs[np.argsort(unique_cs_concs)[::-1]]
            projects_present = cs_filtered_metadata["project"].unique()
            if(len(projects_present)>1):
                cur_sp_comments.append("Data from multiple projects. Verify protocols.")
            else:
                cur_sp_comments.append("")
            lg_conc_replicates = []
            conc_to_fit = []
            for k in range(len(unique_cs_concs)):
                if(unique_cs_concs[k] == 0):
                    continue
                lg_selected_conc = cs_filtered_metadata[cs_filtered_metadata["cs_conc"] == unique_cs_concs[k]]["linegroup"].unique()
                lg_conc_replicates.append(lg_selected_conc)
                conc_to_fit.append(unique_cs_concs[k])

            cur_species_concs.append(conc_to_fit)
            cur_sp_lg_replicates.append(lg_conc_replicates)
        concentrations_present.append(cur_species_concs)
        lg_replicates.append(cur_sp_lg_replicates)
        fitting_comments.append(cur_sp_comments)

    return species_selected, carbon_source_selected, concentrations_present, lg_replicates, fitting_comments

def get_n0(measurement):
    return measurement[np.where(measurement > 0)[0][0]]

def get_yield(measurement, c0):
    return (np.max(measurement) - np.min(measurement))/c0

def monod(y, t, v, Km, q):
    n, c = y
    with np.errstate(divide="raise", invalid="raise"):
        try:
            dndt = v * c / (Km + c) * n
            dcdt = -v * c / (Km + c) * n / q
        except FloatingPointError:
            print(v,Km,n,c,t)
            # np.save("bad_params", [v,Km])
            dndt = v * c / (Km + c) * n
            dcdt = -v * c / (Km + c) * n / q

    return np.array([dndt, dcdt])

def simulate_monod_Km(Km,args):
    v,t,q,n,c0,n0= args
    y = odeint(monod, [n0, c0], t, args=(v, Km[0], q))
    error  = np.sum(((n) - (y[:, 0])) ** 2)
    return error

def get_Km(time_values, measurement_values, initial_conc, initial_n, est_growth_rate, total_yield):
    min_err = np.inf
    Km_best = 0
    random_starts = 10
    args  = [est_growth_rate,time_values,total_yield,measurement_values,initial_conc,initial_n]
    for i in range(random_starts):
        random_Km = np.random.uniform(0,20)
        minimization_trial = optimize.minimize(
            simulate_monod_Km,
            random_Km,
            args=(args),
            bounds=((0, 1000),),
        )
        Km = minimization_trial.x
        err = minimization_trial.fun
        if err < min_err:
            min_err = err
            Km_best = Km
    return Km_best[0]


def simulate_monod(params, t, q, n, c0, n0):
    Km,v = params
    error = 0
    for i in range(len(n)):
        # y = odeint(monod, [n0[i], c0[i]], t[i][argmins[i]:argmaxs[i]], args=(v, Km, q[i]))
        # error += np.sum(((n[i][argmins[i]:argmaxs[i]]) - (y[:, 0])) ** 2)
        y = odeint(monod, [1, 1], t[i]*v, args=(1,Km/c0[i], q[i]*c0[i]/n0[i]))
        error += np.sum((n[i]/n0[i]- y[:, 0]) ** 2)
    return error

def get_params(args,random_starts=10):
    t, series, c0, n0, q,achieved_growth_rates = args
    min_err = np.inf
    Km_best, v_best = 0, 0
    for i in range(random_starts):
        random_Km,random_v = np.random.uniform(0.001,20),np.random.uniform(0.05,2)
        minimization_trial = optimize.minimize(
            simulate_monod,
            [random_Km,random_v],
            args=(
                t,
                q,
                series,
                c0,
                n0
            ),
            bounds=((1e-6, 1000),(np.max(achieved_growth_rates),10)),
        )
        Km, v = minimization_trial.x
        err = minimization_trial.fun
        if err < min_err:
            min_err = err
            Km_best, v_best = Km, v
    return v_best, Km_best


def log_likelohood(theta,args):
    t, series, c0, n0,q,argmins,argmaxs = args
    v,Km = theta
    error = 0
    for i in range(len(n0)):
        y = odeint(monod, [1, c0[i]/Km], t[i][argmins[i]:argmaxs[i]]*v, args=(1,1, q[i]*Km/n0[i]))
        error += np.sum(((series[i][argmins[i]:argmaxs[i]]/n0[i])- (y[:, 0])) ** 2)
    return -error 

def log_prior(theta):
    v,Km = theta
    if 0 < Km < 5000 and 0 < v < 100:
        return 0
    return -np.inf

def log_posterior(theta, args):
    prior = log_prior(theta)
    if not np.isfinite(prior):
        return -np.inf
    return prior + log_likelohood(theta, args)


def get_measurement_values(df_data,cur_lgs):
    time_values = df_data[cur_lgs[0]+"_time"].to_numpy()
    measurement_values = np.mean(np.array([df_data[cur_lg+"_measurement"].to_numpy() for cur_lg in cur_lgs]),axis=0)
    return time_values, measurement_values

def preprocess_measurement(df_data,cur_lgs):
    time_values, measurement_values = get_measurement_values(df_data,cur_lgs)

    non_nan_time_index = np.where(~np.isnan(time_values))[0]
    time_values = time_values[non_nan_time_index]
    measurement_values = measurement_values[non_nan_time_index]

    non_nan_measurement_index = np.where(~np.isnan(measurement_values))[0]
    time_values = time_values[non_nan_measurement_index]
    measurement_values = measurement_values[non_nan_measurement_index]

    measurement_values = gaussian_filter1d(measurement_values, sigma=1)

    return time_values, measurement_values

def get_args(time_values,measurement_values,original_conc,yield_fraction):
    cur_yield = get_yield(measurement_values,original_conc)
    cur_n0 = get_n0(measurement_values)

    custom_yield = cur_yield*yield_fraction
    min_time_index = np.where((measurement_values - cur_n0)/original_conc > custom_yield)[0][0]
    max_time_index = np.argmax(measurement_values)

    cur_time = time_values[min_time_index:max_time_index]
    cur_measurement = measurement_values[min_time_index:max_time_index]

    cur_n0 = cur_measurement[0]
    cur_conc = original_conc*(1-yield_fraction)

    return cur_time, cur_measurement, cur_conc, cur_n0, cur_yield

def est_vmax(time_values,measurement_values):
    return np.max(np.diff(np.log(measurement_values))/np.diff(time_values))

def append_to_args(args_dict,time_values, measurement_values, cur_conc,yield_fraction):
    cur_time, cur_measurement, cur_conc, cur_n0, cur_yield = get_args(time_values,measurement_values,cur_conc,yield_fraction)
    achieved_growth_rate = est_vmax(cur_time,cur_measurement)

    args_dict["t_array"].append(cur_time)
    args_dict["n_array"].append(cur_measurement)
    args_dict["c0_array"].append(cur_conc)
    args_dict["n0_array"].append(cur_n0)
    args_dict["yield_array"].append(cur_yield)
    args_dict["achieved_v_array"].append(achieved_growth_rate)
    return args_dict

def params_from_args(args_dict,run_samples):
    t_array_run = [args_dict["t_array"][i] for i in run_samples]
    n_array_run = [args_dict["n_array"][i] for i in run_samples]
    c0_array_run = [args_dict["c0_array"][i] for i in run_samples]
    n0_array_run = [args_dict["n0_array"][i] for i in run_samples]
    yield_array_run = [args_dict["yield_array"][i] for i in run_samples]
    achieved_v_array_run = [args_dict["achieved_v_array"][i] for i in run_samples]

    args = [t_array_run,n_array_run,c0_array_run,n0_array_run,yield_array_run,achieved_v_array_run]

    # fitting_method = "monod_fit" # "mcmc" , "monod_fit", "minimize", "inidividual"
    
    v_est,Km_est = get_params(args,random_starts=10)

    # Km_est = []
    # for i in range(len(run_samples)):
    #     Km_est.append(get_Km(t_array_run[i],n_array_run[i],c0_array_run[i],n0_array_run[i],achieved_v_array_run[i],yield_array_run[i]))
    # v_est = achieved_v_array_run

    # plt.plot(c0_array_run,achieved_v_array_run,"o")
    # plt.show()

    # monod_growth = lambda x,v,km: x*v/(km+x)
    # monod_fit = optimize.curve_fit(monod_growth, c0_array_run, achieved_v_array_run, p0=[1,1],bounds=([0,0],[10,1000]))
    # v_est,Km_est = monod_fit[0]

    return v_est,Km_est

def generate_run_samples(used_conc):
    conc_num = len(used_conc)
    if(conc_num == 2):
        run_samples = used_conc
    if(conc_num == 3):
        run_samples = used_conc[1:]
    if(conc_num > 3):
        run_samples = used_conc[1:-1]
    if(conc_num > 5):
        run_samples = used_conc[2:-2]
    if(conc_num > 7):
        run_samples = used_conc[4:-2]        
    return run_samples


def main_fit_function(df_data,concentrations_present,lg_replicates,fitting_comments):
    dfs_fitted = []
    fit_values = []

    spNum = len(lg_replicates)
    for i in range(spNum):
        df_sp_fit = []
        val_sp_fit = []
        csNum = len(lg_replicates[i])
        for j in range(csNum):
            df_cs_fit = []
            concNum = len(lg_replicates[i][j])

            if(concNum==0):
                df_sp_fit.append([])
                val_sp_fit.append([])

            elif(concNum ==1):
                original_conc = concentrations_present[i][j][0]
                cur_lgs = lg_replicates[i][j][0]

                time_values, measurement_values = preprocess_measurement(df_data,cur_lgs)

                if(np.max(measurement_values) < 0.05):
                    df_sp_fit.append([])
                    val_sp_fit.append([])
                    continue

                yield_fraction = 0.02
                cur_time, cur_measurement, cur_conc, cur_n0, cur_yield = get_args(time_values, measurement_values, original_conc,yield_fraction)

                cur_v_est = est_vmax(cur_time,cur_measurement)
                cur_Km_est= get_Km(cur_time, cur_measurement, cur_conc, cur_n0, cur_v_est, cur_yield)
                
                cur_simulation = odeint(monod, [cur_n0,cur_conc],cur_time - cur_time[0],args=(cur_v_est, cur_Km_est, cur_yield))
                simulation_df = pd.DataFrame({"time":  cur_time, "measurement": cur_simulation[:,0]})

                df_sp_fit.append([simulation_df])
                val_sp_fit.append([cur_v_est, cur_Km_est])

                fitting_comments[i][j] += "Single concentration fit."

            elif(concNum > 1):
                args_dict = {"t_array": [], "n_array": [], "c0_array": [], "n0_array": [], "yield_array": [], "achieved_v_array": []}
                used_conc = []
                for k in range(concNum):
                    cur_conc = concentrations_present[i][j][k]
                    cur_lgs = lg_replicates[i][j][k]
                    
                    time_values, measurement_values = preprocess_measurement(df_data,cur_lgs)
                    if(np.max(measurement_values) < 0.05):
                        continue
                    used_conc.append(k)
                    yield_fraction = 0.05
                    args_dict = append_to_args(args_dict,time_values, measurement_values, cur_conc,yield_fraction)
                
                # run_samples = generate_run_samples(used_conc)
                run_samples = used_conc
                v_est,Km_est = params_from_args(args_dict,run_samples)

                for k in range(concNum):
                    if(k not in used_conc):
                        df_cs_fit.append([])
                        continue
                    
                    simulated_df = pd.DataFrame({"time": args_dict["t_array"][k], "measurement": odeint(monod, [args_dict["n0_array"][k],args_dict["c0_array"][k]], args_dict["t_array"][k] - args_dict["t_array"][k][0],args=(v_est, Km_est, args_dict["yield_array"][k]))[:,0]})

                    df_cs_fit.append(simulated_df)

                df_sp_fit.append(df_cs_fit)
                val_sp_fit.append([v_est,Km_est])
        dfs_fitted.append(df_sp_fit)
        fit_values.append(val_sp_fit)

    return dfs_fitted,fit_values,fitting_comments

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'
    plt.close(fig)
    return fig_bar_matplotlib

def generate_figure(df_data,cur_df,concentrations,linegroups):
    color_conc = ["C1","C3","C5","C7","C9","C2","C4","C6","C8","C0"]
    fig,ax = plt.subplots(figsize=(10,6))
    skipped_conc = 0
    for k in range(len(concentrations)):
        cur_conc = concentrations[k]
        cur_lgs = linegroups[k]
        if(len(cur_df[k]) == 0):
            skipped_conc += 1
            continue
        time_values = df_data[cur_lgs[0]+"_time"].to_numpy()
        measurement_values = np.mean(np.array([df_data[cur_lg+"_measurement"].to_numpy() for cur_lg in cur_lgs]),axis=0)

        actual_k = k - skipped_conc
        ax.plot(time_values,measurement_values,color=color_conc[actual_k%len(color_conc)],lw=1)
        ax.plot(cur_df[actual_k]["time"], cur_df[actual_k]["measurement"],color=color_conc[actual_k%len(color_conc)],ls="--",label="{:.3f}".format(cur_conc))

        ax.set_xlabel("Time (h)")
        ax.set_ylabel("OD600")
        ax.legend(fontsize=12,loc="lower right")
        ax.set_xlim(0,)

    return fig_to_base64(fig)

                

def table_generator(df_data,df_metadata):
    species_selected, carbon_source_selected,concentrations_present,lg_replicates,fitting_comments = restructure_metadata_fitting(df_metadata) 
    dfs_fitted,fit_values,fitting_comments = main_fit_function(df_data,concentrations_present,lg_replicates,fitting_comments)
    table_header = [html.Thead(html.Tr([html.Th("Species"),html.Th("Carbon Source"),html.Th("v_max"),html.Th("Km"),html.Th("Fits"),html.Th("Comments")]))]

    for i in range(len(species_selected)):
        cur_species = species_selected[i]
        for j in range(len(carbon_source_selected)):
            cur_cs = carbon_source_selected[j]
            if(len(concentrations_present[i][j]) == 0):
                continue
            
            else:
                cur_df = dfs_fitted[i][j]
                if(len(cur_df) == 0):
                    continue
                vmax_table,Km_table = np.round(fit_values[i][j][0],4),np.round(fit_values[i][j][1],4)
                comments = fitting_comments[i][j]
                fig_base64 = generate_figure(df_data,cur_df,concentrations_present[i][j],lg_replicates[i][j])

                table_header.append(html.Tbody(html.Tr([html.Td(cur_species),html.Td(cur_cs),html.Td(vmax_table),html.Td(Km_table),html.Td(html.Img(src=fig_base64,style={"width":"20vw"})),html.Td(comments)])))

    table = dbc.Table(table_header,bordered=True,striped=True,hover=True,responsive=True)

    return table
            
                
