import numpy as np

# ---------------------------------------------------------------------------------------------------------------
# Funções que fazem o cálculo das riscas a ser plotadas FALTA: Mal explicado e sem comentários nas funções em si
def G(T, energy, intens, res, width):
    """ Return Gaussian line shape at x with HWHM alpha """
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) \
            * np.exp(-((T[i] - energy) / (res + width)) ** 2 * np.log(2))
    return (y)


def L(T, energy, intens, res, width):
    """ Return Lorentzian line shape at x with HWHM gamma """
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * (0.5 * (width + res) / np.pi) / \
            ((T[i] - energy) ** 2 + (0.5 * (width + res)) ** 2)
        # y[i]=(intens*2*(width+res)) / (np.pi*(4*(T[i]-energy)**2 + (width+res)**2))
    return (y)


def V(T, energy, intens, res, width):
    """ Return the Voigt line shape at x with Lorentzian component HWHM gamma and Gaussian component HWHM alpha."""
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        sigma = res / np.sqrt(2 * np.log(2))
        y[i] = np.real(intens * wofz(complex(T[i] - energy, width/2) / sigma / np.sqrt(2))) / sigma \
            / np.sqrt(2 * np.pi)
    return (y)
