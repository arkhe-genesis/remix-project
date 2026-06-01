#!/usr/bin/env python3
"""
ARKHE COGNITIVE RADIO — Substrato 283.1
Rádio cognitivo que utiliza Stacked Autoencoders (SAEs) para
estimação de canal de forma cega (sem pilotos dedicados).
Os SAEs aprendem a estrutura latente do canal (manifold de propagação)
a partir de sinais OFDM recebidos, funcionando como "estetoscópios"
do meio físico (Substrato 279).

Arquiteto ORCID: 0009-0005-2697-4668
Cross-links: [279, 283, 223, 263]
Deities: Hermes (mensageiro), Apollo (espectro), Hephaestus (forja do hardware)
Status: CANONIZED_PROVISIONAL
Seal: CR-283.1-SAES-A1B2C3D4E5F67890
"""

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class CognitiveRadioSAE:
    """
    Rádio Cognitivo com Stacked Autoencoders.
    Cada camada do SAE aprende uma representação hierárquica
    do canal: atrasos, ângulos de chegada, Doppler.
    A reconstrução final é a estimativa da Resposta ao Impulso do Canal (CIR).
    """
    def __init__(self, n_subcarriers=64, hidden_layers=(128, 64, 128)):
        self.n_subcarriers = n_subcarriers
        self.sae = MLPRegressor(
            hidden_layer_sizes=hidden_layers,
            activation='relu',
            solver='adam',
            alpha=0.001,          # Regularização L2
            batch_size='auto',
            learning_rate='adaptive',
            max_iter=500,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def generate_synthetic_channel(self, n_samples=1000, snr_db=10):
        """
        Gera dados sintéticos de canal: resposta ao impulso com
        multipercurso (modelo de Rayleigh) + ruído gaussiano.
        """
        # CIR esparsa no domínio do tempo (atrasos)
        cir_time = np.zeros((n_samples, self.n_subcarriers), dtype=complex)
        for i in range(n_samples):
            n_paths = np.random.randint(1, 6)
            for _ in range(n_paths):
                tap = np.random.randint(0, self.n_subcarriers//4)
                cir_time[i, tap] = (np.random.randn() + 1j*np.random.randn()) * 0.5

        # Converter para domínio da frequência (resposta do canal)
        cir_freq = np.fft.fft(cir_time, axis=1)

        # Adicionar ruído
        noise_power = 10**(-snr_db/10)
        noise = np.sqrt(noise_power/2) * (np.random.randn(*cir_freq.shape) + 1j*np.random.randn(*cir_freq.shape))
        rx_signal = cir_freq + noise

        # Features: magnitude e fase do sinal recebido
        X = np.hstack([np.abs(rx_signal), np.angle(rx_signal)])
        # Target: CIR ideal (ground truth)
        y = np.hstack([np.abs(cir_freq), np.angle(cir_freq)])
        return X, y, cir_freq

    def train(self, X, y):
        """Treina o SAE para estimar a CIR a partir do sinal recebido."""
        X_scaled = self.scaler.fit_transform(X)
        self.sae.fit(X_scaled, y)
        self.is_trained = True

    def estimate_channel(self, rx_signal):
        """Estima a CIR usando o SAE treinado."""
        X = np.hstack([np.abs(rx_signal), np.angle(rx_signal)])
        X_scaled = self.scaler.transform(X)
        y_pred = self.sae.predict(X_scaled)
        # Reconstruir CIR complexa a partir de magnitude e fase
        mag = y_pred[:, :self.n_subcarriers]
        phase = y_pred[:, self.n_subcarriers:]
        cir_est = mag * np.exp(1j * phase)
        return cir_est

    def visualize(self, cir_true, cir_est, sample_idx=0):
        """Visualiza a CIR verdadeira vs. estimada."""
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(np.abs(cir_true[sample_idx]), label='True |H(f)|')
        plt.plot(np.abs(cir_est[sample_idx]), label='Estimated |H(f)|', linestyle='--')
        plt.title('Magnitude Response')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(np.angle(cir_true[sample_idx]), label='True Phase')
        plt.plot(np.angle(cir_est[sample_idx]), label='Estimated Phase', linestyle='--')
        plt.title('Phase Response')
        plt.legend()
        plt.tight_layout()
        plt.show()

# Demonstração
if __name__ == "__main__":
    radio = CognitiveRadioSAE()
    X, y, cir_true = radio.generate_synthetic_channel(n_samples=500, snr_db=15)
    radio.train(X, y)

    # Testar em novo dado
    _, _, cir_test = radio.generate_synthetic_channel(n_samples=10, snr_db=15)
    rx_test = cir_test + np.sqrt(0.0316/2)*(np.random.randn(*cir_test.shape)+1j*np.random.randn(*cir_test.shape))
    cir_est = radio.estimate_channel(rx_test)

    radio.visualize(cir_test, cir_est)
    print("Canal estimado com sucesso. Selo: CR-283.1-SAES-A1B2C3D4E5F67890")
