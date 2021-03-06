
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import random
import pickle
from scipy import stats

proteomes = ['UP000002311_Scerevisiae_NoIsoforms', 'UP000001940_6239_Celegans_NoIsoforms', 'UP000000803_7227_Dmelanogaster_NoIsoforms', 'UP000000437_7955_Drerio_NoIsoforms', 'UP000186698_8355_Xlaevis_NoIsoforms', 'UP000000589_10090_Mmusculus_NoIsoforms', 'UP000005640_9606_Hsapiens_NoIsoforms']
abbrevs = ['Scerevisiae', 'Celegans', 'Dmelanogaster', 'Drerio', 'Xlaevis', 'Mmusculus', 'Hsapiens']
amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
aa_names = {'A':'Alanine (A)', 'C':'Cysteine (C)', 'D':'Aspartic Acid (D)', 'E':'Glutamic Acid (E)',
        'F':'Phenylalanine (F)', 'G':'Glycine (G)', 'H':'Histidine (H)', 'I':'Isoleucine (I)', 
        'K':'Lysine (K)', 'L':'Leucine (L)', 'M':'Methionine (M)', 'N':'Asparagine (N)',
        'P':'Proline (P)', 'Q':'Glutamine (Q)', 'R':'Arginine (R)', 'S':'Serine (S)',
        'T':'Threonine (T)', 'V':'Valine (V)', 'W':'Tryptophan (W)','Y':'Tyrosine (Y)'}
        
def main():

    df = {'Proteome':[],
        'GO term':[],
        'Amino Acid':[],
        'GO ID':[],
        'Category':[]
        }
        
    for aa in amino_acids:
        all_go_hits = []
        for i in range(len(proteomes)):
            
            # SKIPS LCD CATEGORY IF NO LCDs OF THAT CATEGORY WERE OBSERVED IN THE ORGANISM
            try:
                h = open(abbrevs[i] + '_' + aa + '_GO_RESULTS.tsv')
            except:
                continue
            header = h.readline()
            for line in h:
                items = line.rstrip().split('\t')
                if len(items) == 13:
                    go_id, cat, e_or_p, go_desc, ratio_in_list, ratio_in_pop, uncorr_pval, depth, num_prots, bonf_pval, sidak_pval, holm_pval, assoc_prots = items    #lines with 'p' for e_or_p sometimes do not have any proteins in the last cell
                else:
                    go_id, cat, e_or_p, go_desc, ratio_in_list, ratio_in_pop, uncorr_pval, depth, num_prots, bonf_pval, sidak_pval, holm_pval = items
                
                if e_or_p == 'e' and float(sidak_pval) < 0.05:
                    df['Proteome'].append( abbrevs[i] )
                    df['GO term'].append( go_desc )
                    df['GO ID'].append( go_id )
                    df['Amino Acid'].append( aa )
                    df['Category'].append( cat )
                
            h.close()
            
    plotting(df)


def count_freqs(df):

    df = pd.DataFrame.from_dict(df)
    
    counts_df = {}
    for aa in amino_acids:
        counts_df[aa] = []
        temp_df = df[df['Amino Acid'] == aa]
        counts = []
        for go_term in temp_df['GO term']:
            counts.append( list(temp_df['GO term']).count(go_term) )
            counts_df[aa].append( list(temp_df['GO term']).count(go_term) )

    for aa in amino_acids:
        if len(counts_df[aa]) == 0:
            continue
        xvals = []
        yvals = []
        for x in range(min(counts_df[aa]), max(counts_df[aa])+1):
            xvals.append(x)
            yvals.append( counts_df[aa].count(x) )
            

def plotting(df):

    sampling_df = get_sampling_data()
        
    aa_index = 1
    fig, ax = plt.subplots(5,4,sharex=True, sharey=False, figsize=(8,10))
    big_subplot = fig.add_subplot(111)
    big_subplot.spines['top'].set_color('none')
    big_subplot.spines['bottom'].set_color('none')
    big_subplot.spines['left'].set_color('none')
    big_subplot.spines['right'].set_color('none')
    big_subplot.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

    df = pd.DataFrame.from_dict(df)
    
    counts_df = {}
    for aa in amino_acids:
        counts_df[aa] = []
        temp_df = df[df['Amino Acid'] == aa]
        counts = []
        for go_term in list(set(temp_df['GO term'])):
            counts.append( list(temp_df['GO term']).count(go_term) )
            counts_df[aa].append( list(temp_df['GO term']).count(go_term) )

    for aa in amino_acids:
        new_df = {'LCD Class':[],
                'Number of Organisms':[],
                'Count':[],
                'Category':[]
                }
        if len(counts_df[aa]) == 0:
            continue
        xvals = []
        yvals = []
        total_obs = 0

        for x in range(1, 8):
            xvals.append(x)
            yvals.append( counts_df[aa].count(x) )
            total_obs += counts_df[aa].count(x)
            new_df['LCD Class'].append( aa )
            new_df['Number of Organisms'].append( x )
            new_df['Count'].append( counts_df[aa].count(x) )
            new_df['Category'].append( 'Observed' )

        #PLOTTING
        ax = plt.subplot(5,4, aa_index)
        sns.barplot(x=xvals, y=yvals, palette=['#1f77b4'])   #PLOT OBSERVED VALUES
        sns.barplot(x=xvals, y=sampling_df[aa]['Means'], palette=['#d62728'], yerr=sampling_df[aa]['SDs'])   #PLOT PROTEIN SAMPLING VALUES
        
        overall_max = ax.patches[0].get_height()
        plt.ylim(0, overall_max + overall_max*0.2)
        plt.ylabel('')
        plt.xlabel('')
        plt.title(aa_names[aa], fontsize=12, fontname='Arial', pad=0.1)
        plt.xlim(-1, 7)
        plt.xticks([x for x in range(8)], labels=[str(x) for x in range(1, 8)], fontname='Arial', fontsize=14)
        
        if aa == 'W':
            plt.yticks([0, 1], labels=['0', '1'], fontname='Arial', fontsize=14)
        elif aa == 'F':
            plt.yticks([0, 2, 4, 6, 8, 10], labels=['0', '2', '4', '6', '8', '10'], fontname='Arial', fontsize=14)
        elif aa == 'M':
            plt.yticks([0, 1, 2], labels=['0', '1', '2'], fontname='Arial', fontsize=14)
        else:
            plt.yticks(fontname='Arial', fontsize=14)

        ax = plt.gca()
        if aa_index in range(1,17):
            ax.set_xticklabels([])

        aa_index += 1

    fig.text(-0.025, 0.5, 'Frequency (Number of Enriched GO Terms)', va='center', rotation='vertical', fontname='Arial', fontsize=16)
    fig.text(0.5, -0.02, 'Number of Organisms Sharing Enriched GO Term', ha='center', fontname='Arial', fontsize=16)
    plt.tight_layout(pad=0.2)
    plt.savefig('Fig S8 - ModelEukaryoticOrganisms_LENGTH-WEIGHTED_ProteinSampling_GOresults.tiff', bbox_inches ='tight', dpi=600)
    plt.close()  
    
    
def random_go_sampling():

    org_goterm_lists = pickle.load(open('All_Organisms_GOids.dat', 'rb'))
    goterm_counts = get_goterm_counts()
    cross_spec_counts = {1:0,
                    2:0,
                    3:0,
                    4:0,
                    5:0,
                    6:0,
                    7:0
                    }

    cross_spec_counts = {}
    for aa in amino_acids:
        cross_spec_counts[aa] = {1:0,
                        2:0,
                        3:0,
                        4:0,
                        5:0,
                        6:0,
                        7:0
                        }
        for i in range(100000):
            organism_samples = {}
            go_terms = []
            for organism in abbrevs:
                organism_samples[organism] = []
                organism_gos = org_goterm_lists[organism]
                count = goterm_counts[aa][organism]

                go_samp = random.sample(organism_gos, count)
                organism_samples[organism].append( go_samp )
                go_terms += go_samp
                
            for go_term in set(go_terms):
                count = go_terms.count(go_term)
                cross_spec_counts[aa][count] += 1

    return cross_spec_counts
                
                
def get_goterm_counts():
    df = {}
    for aa in amino_acids:
        df[aa] = {}
        for abbrev in abbrevs:
            try:
                h = open(abbrev + '_' + aa + '_GO_RESULTS.tsv')
            except:
                df[aa][abbrev] = 0
                continue
            header = h.readline()
            count = 0
            for line in h:
                items = line.rstrip().split('\t')
                enr_or_pur = items[2]
                p_sidak = float(items[10])
                if enr_or_pur == 'e' and p_sidak < 0.05 + 0.0000000001:
                    count += 1
            h.close()
            
            df[aa][abbrev] = count
            
    return df
    
    
def get_sampling_data():
    
    df = {aa:{'Means':[], 'SDs':[]} for aa in amino_acids}
    h = open('ModelEukaryoticOrganisms_Cross-Organism_GOfrequencies_LENGTH-WEIGHTED_ProteinSampling.csv')
    header = h.readline()
    for line in h:
        lcd_class, num_organisms_cat, ave_num_shared_gos, stddev, stderr, ci = line.rstrip().split(',')
        df[lcd_class]['Means'].append( float(ave_num_shared_gos) )
        df[lcd_class]['SDs'].append( float(stddev) )
    h.close()
        
    return df
        
    
if __name__ == '__main__':
    main()
    