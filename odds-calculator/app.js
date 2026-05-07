document.addEventListener('DOMContentLoaded', () => {
    const BLUE_TAN_WIN_RATES = {
        6: 0.0676,
        7: 0.0596,
        8: 0.0446,
        9: 0.0206
    };

    const state = {
        budget: 10000,
        blueTan: {
            favoriteOdds: 2.5,
            minExpectedRoi: 150,
            minIndexCount: 2
        },
        horses: [
            { id: 1, popularity: 6, odds: 23.0, indexCount: 2 },
            { id: 2, popularity: 7, odds: 28.0, indexCount: 2 }
        ]
    };

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
        syntheticOdds: document.getElementById('synthetic-odds'),
        horseCount: document.getElementById('horse-count'),
        shareBtn: document.getElementById('share-btn'),
        blueTanFavoriteOdds: document.getElementById('blue-tan-favorite-odds'),
        blueTanMinRoi: document.getElementById('blue-tan-min-roi'),
        blueTanMinIndex: document.getElementById('blue-tan-min-index'),
        blueTanStatus: document.getElementById('blue-tan-status'),
        blueTanPick: document.getElementById('blue-tan-pick'),
        blueTanDetail: document.getElementById('blue-tan-detail')
    };

    init();

    function init() {
        bindEvents();
        renderHorses();
        calculate();
    }

    function bindEvents() {
        els.budgetInput.addEventListener('input', (event) => {
            state.budget = parseInt(event.target.value, 10) || 0;
            calculate();
        });

        els.blueTanFavoriteOdds.addEventListener('input', (event) => {
            state.blueTan.favoriteOdds = parseFloat(event.target.value) || 0;
            calculate();
        });

        els.blueTanMinRoi.addEventListener('input', (event) => {
            state.blueTan.minExpectedRoi = parseFloat(event.target.value) || 0;
            calculate();
        });

        els.blueTanMinIndex.addEventListener('input', (event) => {
            state.blueTan.minIndexCount = parseInt(event.target.value, 10) || 0;
            calculate();
        });

        els.addBtn.addEventListener('click', addHorse);
        els.resetBtn.addEventListener('click', resetAll);
        els.shareBtn.addEventListener('click', shareResult);
    }

    function addHorse() {
        const newId = state.horses.length > 0 ? Math.max(...state.horses.map((horse) => horse.id)) + 1 : 1;
        const lastPopularity = state.horses.length > 0 ? state.horses[state.horses.length - 1].popularity : 5;
        state.horses.push({
            id: newId,
            popularity: lastPopularity + 1,
            odds: 0,
            indexCount: 0
        });
        renderHorses();
        calculate();
    }

    function removeHorse(id) {
        state.horses = state.horses.filter((horse) => horse.id !== id);
        renderHorses();
        calculate();
    }

    function updateHorse(id, field, value) {
        const horse = state.horses.find((item) => item.id === id);
        if (!horse) return;

        const numericValue = field === 'popularity' || field === 'indexCount'
            ? parseInt(value, 10) || 0
            : parseFloat(value) || 0;
        horse[field] = numericValue;
        calculate();
    }

    function resetAll() {
        state.budget = 10000;
        state.blueTan.favoriteOdds = 2.5;
        state.blueTan.minExpectedRoi = 150;
        state.blueTan.minIndexCount = 2;
        state.horses = [{ id: 1, popularity: 6, odds: 0, indexCount: 0 }];

        els.budgetInput.value = state.budget;
        els.blueTanFavoriteOdds.value = state.blueTan.favoriteOdds;
        els.blueTanMinRoi.value = state.blueTan.minExpectedRoi;
        els.blueTanMinIndex.value = state.blueTan.minIndexCount;
        renderHorses();
        calculate();
    }

    function renderHorses() {
        els.oddsList.innerHTML = '';
        els.horseCount.textContent = `${state.horses.length}頭`;

        state.horses.forEach((horse) => {
            const row = document.createElement('div');
            row.className = 'horse-row';
            row.dataset.id = String(horse.id);
            row.innerHTML = `
                <input type="number" class="horse-popularity-input" value="${horse.popularity || ''}" min="1" max="18" inputmode="numeric" aria-label="人気">
                <div class="odds-input-group">
                    <input type="number" value="${horse.odds || ''}" step="0.1" min="0" inputmode="decimal" aria-label="単勝オッズ">
                </div>
                <input type="number" class="index-count-input" value="${horse.indexCount || 0}" min="0" max="4" inputmode="numeric" aria-label="指数欄数">
                <div class="calc-result" id="result-${horse.id}">-</div>
                <button class="delete-btn" aria-label="削除" title="削除">×</button>
            `;

            row.querySelector('.horse-popularity-input').addEventListener('input', (event) => {
                updateHorse(horse.id, 'popularity', event.target.value);
            });
            row.querySelector('.odds-input-group input').addEventListener('input', (event) => {
                updateHorse(horse.id, 'odds', event.target.value);
            });
            row.querySelector('.index-count-input').addEventListener('input', (event) => {
                updateHorse(horse.id, 'indexCount', event.target.value);
            });
            row.querySelector('.delete-btn').addEventListener('click', () => removeHorse(horse.id));
            els.oddsList.appendChild(row);
        });
    }

    function validHorses() {
        return state.horses.filter((horse) => horse.odds > 0 && horse.popularity > 0);
    }

    function blueTanExpectedRoi(horse) {
        const winRate = BLUE_TAN_WIN_RATES[horse.popularity] || 0;
        return winRate * horse.odds * 100;
    }

    function findBlueTanPick(horses) {
        if (state.blueTan.favoriteOdds >= 3.0) return null;

        return [...horses]
            .filter((horse) => horse.popularity >= 6 && horse.popularity <= 9)
            .sort((a, b) => a.popularity - b.popularity)
            .find((horse) => (
                blueTanExpectedRoi(horse) >= state.blueTan.minExpectedRoi
                && horse.indexCount >= state.blueTan.minIndexCount
            )) || null;
    }

    function updateBlueTan(horses) {
        const pick = findBlueTanPick(horses);

        if (state.blueTan.favoriteOdds >= 3.0) {
            setBlueTanResult(
                '見送り',
                'skip',
                '1番人気オッズが3.0倍以上',
                '青単は買わず、6〜9番人気を相手候補として扱う条件です。'
            );
            return;
        }

        if (!pick) {
            setBlueTanResult(
                '該当なし',
                'neutral',
                '条件達成馬なし',
                `6〜9番人気、期待回収率${state.blueTan.minExpectedRoi}%以上、指数${state.blueTan.minIndexCount}欄以上を満たす馬がいません。`
            );
            return;
        }

        setBlueTanResult(
            '買い',
            'buy',
            `${pick.popularity}番人気 / 単勝${pick.odds.toFixed(1)}倍`,
            `期待回収率 ${blueTanExpectedRoi(pick).toFixed(1)}% / 指数${pick.indexCount}欄。人気順で最初に該当した1頭です。`
        );
    }

    function setBlueTanResult(status, className, pickText, detailText) {
        els.blueTanStatus.textContent = status;
        els.blueTanStatus.className = `blue-tan-status ${className}`;
        els.blueTanPick.textContent = pickText;
        els.blueTanDetail.textContent = detailText;
    }

    function calculate() {
        const horses = validHorses();
        updateBlueTan(horses);

        if (horses.length === 0 || state.budget <= 0) {
            els.resultSection.classList.add('hidden');
            return;
        }

        const totalImpliedProb = horses.reduce((sum, horse) => sum + (1 / horse.odds), 0);
        const stakes = allocateStakes(horses, totalImpliedProb);
        renderStakeResults(horses, stakes, totalImpliedProb);
    }

    function allocateStakes(horses, totalImpliedProb) {
        const stakes = {};
        let allocatedBudget = 0;

        horses.forEach((horse) => {
            const rawStake = state.budget * ((1 / horse.odds) / totalImpliedProb);
            const stake100 = Math.floor(rawStake / 100) * 100;
            stakes[horse.id] = stake100;
            allocatedBudget += stake100;
        });

        let remainder = state.budget - allocatedBudget;
        while (remainder >= 100) {
            let bestHorseId = null;
            let minPayout = Infinity;

            horses.forEach((horse) => {
                const currentPayout = stakes[horse.id] * horse.odds;
                if (currentPayout < minPayout) {
                    minPayout = currentPayout;
                    bestHorseId = horse.id;
                }
            });

            if (bestHorseId === null) break;
            stakes[bestHorseId] += 100;
            remainder -= 100;
        }

        return stakes;
    }

    function renderStakeResults(horses, stakes, totalImpliedProb) {
        let minPayout = Infinity;
        let maxPayout = -Infinity;
        let totalInvestment = 0;

        const blueTanPick = findBlueTanPick(horses);

        horses.forEach((horse) => {
            const stake = stakes[horse.id] || 0;
            const payout = Math.floor(stake * horse.odds);
            totalInvestment += stake;
            minPayout = Math.min(minPayout, payout);
            maxPayout = Math.max(maxPayout, payout);

            const resultEl = document.getElementById(`result-${horse.id}`);
            const rowEl = document.querySelector(`.horse-row[data-id="${horse.id}"]`);
            if (rowEl) rowEl.classList.toggle('blue-tan-pick', Boolean(blueTanPick && blueTanPick.id === horse.id));
            if (!resultEl) return;

            resultEl.innerHTML = stake > 0
                ? `<strong>${stake.toLocaleString()}</strong><small>円 / 払戻${payout.toLocaleString()}</small>`
                : '<span class="muted">対象外</span>';
        });

        if (totalInvestment <= 0) {
            els.resultSection.classList.add('hidden');
            return;
        }

        const minProfit = minPayout - totalInvestment;
        els.resultSection.classList.remove('hidden');
        els.totalInvestment.textContent = totalInvestment.toLocaleString();
        els.expectedPayout.textContent = minPayout === maxPayout
            ? minPayout.toLocaleString()
            : `${minPayout.toLocaleString()}〜`;
        els.expectedProfit.textContent = `${minProfit >= 0 ? '+' : ''}${minProfit.toLocaleString()}`;
        els.expectedProfit.style.color = minProfit < 0 ? 'var(--danger)' : 'var(--accent)';
        els.returnRate.textContent = Math.round((minPayout / totalInvestment) * 100);
        els.syntheticOdds.textContent = (1 / totalImpliedProb).toFixed(2);
    }

    function shareResult() {
        const horses = validHorses();
        if (horses.length === 0) return;

        const totalImpliedProb = horses.reduce((sum, horse) => sum + (1 / horse.odds), 0);
        const stakes = allocateStakes(horses, totalImpliedProb);
        const blueTanPick = findBlueTanPick(horses);
        const minPayout = Math.min(...horses.map((horse) => Math.floor(stakes[horse.id] * horse.odds)));
        const totalInvestment = horses.reduce((sum, horse) => sum + (stakes[horse.id] || 0), 0);
        const profit = minPayout - totalInvestment;

        const lines = [
            '競馬 合成オッズ計算',
            `予算: ${state.budget.toLocaleString()}円`,
            `合成オッズ: ${(1 / totalImpliedProb).toFixed(2)}倍`,
            `最低利益: ${profit >= 0 ? '+' : ''}${profit.toLocaleString()}円`,
            blueTanPick ? `青単: ${blueTanPick.popularity}番人気 ${blueTanPick.odds.toFixed(1)}倍` : '青単: 見送り/該当なし',
            '',
            ...horses.map((horse) => `${horse.popularity}番人気 ${horse.odds}倍 -> ${stakes[horse.id].toLocaleString()}円`)
        ];

        const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(lines.join('\n'))}`;
        window.open(shareUrl, '_blank');
    }
});
