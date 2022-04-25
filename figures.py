import torch
from sklearn.model_selection import train_test_split
from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from pylab import *

from grm import GRMEstimator
from utils import manual_seed, invert_factors


def screeplot(latent_sizes:             List[int], # need to sort these if they're not
              data:                     torch.Tensor,
              n_cats:                   List[int],
              test_size:                float,
              inference_net_sizes_list: List[List[int]],
              learning_rates:           List[float],
              missing_mask:             Optional[torch.Tensor] = None,
              max_epochs:               int = 100000,
              batch_size:               int = 32,
              device:                   torch.device = "cpu",
              log_interval:             int = 100,
              iw_samples_fit:           int = 1,
              iw_samples_ll:            int = 5000,
              random_seed:              int = 1,
              xlabel:                   str = "Number of Factors",
              ylabel:                   str = "Predicted Approximate Negative Log-Likelihood",
              title:                    str = "Approximate Log-Likelihood Scree Plot",
             ):
    """"""
    assert(test_size > 0 and test_size < 1)
    data_train, data_test = train_test_split(data, train_size = 1 - test_size, test_size = test_size)
    n_items = data.size(1)
            
    manual_seed(random_seed)
    ll_list = []
    for idx, latent_size in enumerate(latent_sizes):
        print("\nLatent size = ", latent_size, end="\n")
        model = GRMEstimator(input_size = n_items,
                             inference_net_sizes = inference_net_sizes_list[idx],
                             latent_size = latent_size,
                             n_cats = n_cats,
                             learning_rate = learning_rates[idx],
                             device = device,
                             log_interval = log_interval,
                            )
        model.fit(data, batch_size, missing_mask, max_epochs, iw_samples = iw_samples_fit)

        ll = model.log_likelihood(data_test, iw_samples = iw_samples_ll)
        ll_list.append(ll)
        
    fig, ax = plt.subplots(constrained_layout = True)
    fig.set_size_inches(5, 5, forward = True)
    fig.set_size_inches(5, 5, forward = True)
    
    ax.plot(latent_sizes, [ll for ll in ll_list], "k-o")
    
    ax.set_xticks(np.arange(min(latent_sizes) - 1, max(latent_sizes) + 2).tolist())
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    fig.suptitle(title)
    fig.show()

    pdf = matplotlib.backends.backend_pdf.PdfPages("scree_plot.pdf")
    pdf.savefig(fig, dpi = 300)
    pdf.close()
    
    return ll_list

    
def loadings_heatmap(loadings:     np.ndarray,
                     x_label:      str = "Factor", 
                     y_label:      str = "Item", 
                     title:        str = "Factor Loadings"):
    latent_size = loadings.shape[1]
    
    c = pcolor(invert_factors(loadings))
    set_cmap("gray_r")
    colorbar() 
    c = pcolor(invert_factors(loadings), edgecolors = "w", linewidths = 1, vmin = 0) 
    xlabel(x_label)
    ylabel(y_label)
    xticks(np.arange(latent_size) + 0.5,
           [str(size + 1) for size in range(latent_size)])
    ytick_vals = [int(10 * (size + 1)) for size in range(latent_size)]
    yticks(np.array(ytick_vals) - 0.5, [str(val) for val in ytick_vals])
    plt.gca().invert_yaxis()
    suptitle(title, y = 0.93)
    
    plt.savefig("loadings_heatmap.pdf")
    plt.show()