document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    const state = {
        budget: 10000,
        horses: [
            { id: 1, num: 1, odds: 2.5 },
            { id: 2, num: 2, odds: 5.0 }
        ]
    };

    // --- DOM Elements ---
    const els = {
        budgetInput: document.getElementById('total-budget'),
        oddsList: document.getElementById('odds-list'),
        addBtn: document.getElementById('add-horse-btn'),
        resetBtn: document.getElementById('reset-btn'),
        resultSection: document.getElementById('result-section'),
        expectedPayout: document.getElementById('expected-payout'),
        totalInvestment: document.getElementById('total-investment'),
        expectedProfit: document.getElementById('expected-profit'),
        returnRate: document.getElementById('return-rate'),
        horseCount: document.getElementById('horse-count'),
        shareBtn: document.getElementById('share-btn')
    };

    // --- Init ---
    init();

    function init() {
        renderHorses();
        calculate();

        // Event Listeners
        els.budgetInput.addEventListener('input', (e) => {
            state.budget = parseInt(e.target.value) || 0;
            calculate();
        });

        els.addBtn.addEventListener('click', addHorse);
        els.resetBtn.addEventListener('click', resetAll);
        if (els.shareBtn) els.shareBtn.addEventListener('click', shareResult);
    }

    // --- Actions ---
    function addHorse() {
        const newId = (state.horses.length > 0 ? Math.max(...state.horses.map(h => h.id)) : 0) + 1;
        const lastNum = state.horses.length > 0 ? state.horses[state.horses.length - 1].num : 0;

        state.horses.push({
            id: newId,
            num: lastNum + 1,
            odds: 0
        });
        renderHorses();
        calculate();
    }

    function removeHorse(id) {
        state.horses = state.horses.filter(h => h.id !== id);
        renderHorses();
        calculate();
    }

    function updateHorse(id, field, value) {
        const horse = state.horses.find(h => h.id === id);
        if (horse) {
            horse[field] = parseFloat(value);
            calculate();
        }
    }

    function resetAll() {
        if (!confirm('全ての入力をリセットしますか？')) return;
        state.budget = 10000;
        state.horses = [
            { id: 1, num: 1, odds: 0 }
        ];
        els.budgetInput.value = state.budget;
        renderHorses();
        calculate();
    }

    // --- Rendering ---
    function renderHorses() {
        els.oddsList.innerHTML = '';
        els.horseCount.textContent = `${state.horses.length}頭`;

        state.horses.forEach((horse) => {
            const row = document.createElement('div');
            row.className = 'horse-row';
            row.innerHTML = `
                <input type="number" class="horse-num-input" value="${horse.num}" placeholder="#" 
                    onchange="app.updateHorse(${horse.id}, 'num', this.value)">
                
                <div class="odds-input-group">
                    <input type="number" value="${horse.odds || ''}" step="0.1" inputmode="decimal" placeholder="オッズ"
                        oninput="app.updateHorse(${horse.id}, 'odds', this.value)">
                </div>

                <div class="calc-result" id="result-${horse.id}">
                    -
                </div>

                <button class="delete-btn" aria-label="削除" onclick="app.removeHorse(${horse.id})">
                    ×
                </button>
            `;
            els.oddsList.appendChild(row);
        });
    }

    // --- Calculation Logic ---
    function calculate() {
        const validHorses = state.horses.filter(h => h.odds > 0);
        if (validHorses.length === 0 || state.budget <= 0) {
            els.resultSection.classList.add('hidden');
            return;
        }

        // 1. Implied Probabilities
        let totalImpliedProb = 0;
        validHorses.forEach(h => {
            h.ip = 1 / h.odds;
            totalImpliedProb += h.ip;
        });

        let allocatedBudget = 0;
        const results = {};

        // 2. Allocate base stakes (floored to 100)
        validHorses.forEach(h => {
            let rawStake = state.budget * (h.ip / totalImpliedProb);
            let stake100 = Math.floor(rawStake / 100) * 100;
            results[h.id] = stake100;
            allocatedBudget += stake100;
        });

        // 3. Distribute Remainder
        let remainder = state.budget - allocatedBudget;

        while (remainder >= 100) {
            let bestHorseId = -1;
            let minPayout = Infinity;

            validHorses.forEach(h => {
                const currentPayout = results[h.id] * h.odds;
                if (currentPayout < minPayout) {
                    minPayout = currentPayout;
                    bestHorseId = h.id;
                }
            });

            if (bestHorseId !== -1) {
                results[bestHorseId] += 100;
                remainder -= 100;
            } else {
                break;
            }
        }

        // --- Render Results ---
        let minExpReturn = Infinity;
        let maxExpReturn = -Infinity;
        let totalInvest = 0;

        validHorses.forEach(h => {
            const stake = results[h.id];
            totalInvest += stake;
            const payout = Math.floor(stake * h.odds);

            if (payout < minExpReturn) minExpReturn = payout;
            if (payout > maxExpReturn) maxExpReturn = payout;

            const resEl = document.getElementById(`result-${h.id}`);
            if (resEl) {
                if (stake > 0) {
                    // Update: Show stake clearly and expected return small
                    resEl.innerHTML = `
                        <span style="font-size:1.1em; color:white">${stake.toLocaleString()}</span>
                        <span style="font-size:0.7em">円</span><br>
                        <span style="color:#888;font-size:0.7em">払:${payout.toLocaleString()}</span>
                    `;
                } else {
                    resEl.innerHTML = `<span style="color:#555;font-size:0.8em">対象外</span>`;
                }
            }
        });

        if (totalInvest <= 0) {
            els.resultSection.classList.add('hidden');
            return;
        }

        els.resultSection.classList.remove('hidden');
        els.totalInvestment.textContent = totalInvest.toLocaleString();

        if (minExpReturn !== maxExpReturn) {
            els.expectedPayout.textContent = `${minExpReturn.toLocaleString()}~`;
        } else {
            els.expectedPayout.textContent = minExpReturn.toLocaleString();
        }

        const minProfit = minExpReturn - totalInvest;
        els.expectedProfit.textContent = (minProfit >= 0 ? '+' : '') + minProfit.toLocaleString();
        els.expectedProfit.style.color = minProfit < 0 ? 'var(--danger)' : 'var(--accent)';

        const rate = Math.round((minExpReturn / totalInvest) * 100);
        els.returnRate.textContent = rate;
    }

    function shareResult() {
        const validHorses = state.horses.filter(h => h.odds > 0);
        if (validHorses.length === 0) return;

        let text = `🐴 競馬資金配分\n💰 予算: ${state.budget.toLocaleString()}円\n\n`;

        // Re-calculate simply for text generation
        let totalImpliedProb = 0;
        validHorses.forEach(h => totalImpliedProb += (1 / h.odds));

        let allocated = 0;
        const results = {};
        validHorses.forEach(h => {
            let raw = state.budget * ((1 / h.odds) / totalImpliedProb);
            let val = Math.floor(raw / 100) * 100;
            results[h.id] = val;
            allocated += val;
        });

        // Distribute remainder (simple version for text)
        let remainder = state.budget - allocated;
        // Naive distribution for text match: just add to first few
        // Note: This might slightly differ from exact logic but good enough for share text
        // or we can implement exact logic. Let's try to match exact logic quickly.
        while (remainder >= 100) {
            let bestId = -1; let minP = Infinity;
            validHorses.forEach(h => {
                let p = results[h.id] * h.odds;
                if (p < minP) { minP = p; bestId = h.id; }
            });
            if (bestId !== -1) { results[bestId] += 100; remainder -= 100; }
            else break;
        }

        validHorses.forEach((h, i) => {
            const stake = results[h.id];
            text += `#${h.num} (${h.odds}倍) → ${stake.toLocaleString()}円\n`;
        });

        const minPayout = Math.min(...validHorses.map(h => Math.floor(results[h.id] * h.odds)));
        const profit = minPayout - state.budget;

        text += `\n🎯 予想利益: ${profit >= 0 ? '+' : ''}${profit.toLocaleString()}円\n`;
        text += `#競馬 #オッズ計算 #資金配分`;

        const url = "https://keny0823.github.io/kakuyasu-simlab/odds-calculator/";
        const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;

        window.open(shareUrl, '_blank');
    }

    window.app = { addHorse, removeHorse, updateHorse, resetAll };
});
