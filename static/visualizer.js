/* ==========================================================
   Sorting Visualizer
   Every algorithm sorts the SAME input array, side by side.
   Each algorithm is a generator: one `yield` = one visible step
   (a comparison or an array write), so all panels advance in
   lockstep and the one needing fewer steps finishes first.
   ========================================================== */

(function (root) {

    // ------------------------------------------------------
    // Helpers
    // ------------------------------------------------------

    function* swap(a, i, j, c) {
        const t = a[i]; a[i] = a[j]; a[j] = t;
        c.wr += 2;
        c.hl = { write: [i, j] };
        yield;
    }

    // ------------------------------------------------------
    // Algorithms (generators)
    // ------------------------------------------------------

    function* bubble(a, c) {
        const n = a.length;
        for (let i = 0; i < n; i++) {
            let swapped = false;
            for (let j = 0; j < n - i - 1; j++) {
                c.cmp++; c.hl = { cmp: [j, j + 1] }; yield;
                if (a[j] > a[j + 1]) {
                    yield* swap(a, j, j + 1, c);
                    swapped = true;
                }
            }
            c.sorted[n - i - 1] = 1;
            if (!swapped) { c.sorted.fill(1); break; }
        }
    }

    function* selection(a, c) {
        const n = a.length;
        for (let i = 0; i < n; i++) {
            let m = i;
            for (let j = i + 1; j < n; j++) {
                c.cmp++; c.hl = { cmp: [j, m], pivot: [i] }; yield;
                if (a[j] < a[m]) m = j;
            }
            if (m !== i) yield* swap(a, i, m, c);
            c.sorted[i] = 1;
        }
    }

    function* insertion(a, c) {
        for (let i = 1; i < a.length; i++) {
            const key = a[i];
            let j = i - 1;
            while (j >= 0) {
                c.cmp++; c.hl = { cmp: [j, j + 1] }; yield;
                if (a[j] > key) {
                    a[j + 1] = a[j]; c.wr++;
                    c.hl = { write: [j + 1] }; yield;
                    j--;
                } else break;
            }
            if (j + 1 !== i) {
                a[j + 1] = key; c.wr++;
                c.hl = { write: [j + 1] }; yield;
            }
        }
    }

    function* merge(a, c) {
        function* ms(lo, hi) {                // [lo, hi)
            if (hi - lo <= 1) return;
            const mid = (lo + hi) >> 1;
            yield* ms(lo, mid);
            yield* ms(mid, hi);

            const L = a.slice(lo, mid), R = a.slice(mid, hi);
            let i = 0, j = 0, k = lo;
            while (i < L.length && j < R.length) {
                c.cmp++; c.hl = { cmp: [lo + i, mid + j], zone: [lo, hi - 1] }; yield;
                a[k] = (L[i] <= R[j]) ? L[i++] : R[j++];
                c.wr++; c.hl = { write: [k], zone: [lo, hi - 1] }; yield;
                k++;
            }
            while (i < L.length) {
                a[k] = L[i++]; c.wr++;
                c.hl = { write: [k], zone: [lo, hi - 1] }; yield; k++;
            }
            while (j < R.length) {
                a[k] = R[j++]; c.wr++;
                c.hl = { write: [k], zone: [lo, hi - 1] }; yield; k++;
            }
        }
        yield* ms(0, a.length);
    }

    function* heap(a, c) {
        const n = a.length;

        function* heapify(len, root) {
            let largest = root;
            const l = 2 * root + 1, r = 2 * root + 2;
            if (l < len) {
                c.cmp++; c.hl = { cmp: [l, largest] }; yield;
                if (a[l] > a[largest]) largest = l;
            }
            if (r < len) {
                c.cmp++; c.hl = { cmp: [r, largest] }; yield;
                if (a[r] > a[largest]) largest = r;
            }
            if (largest !== root) {
                yield* swap(a, root, largest, c);
                yield* heapify(len, largest);
            }
        }

        for (let i = (n >> 1) - 1; i >= 0; i--) yield* heapify(n, i);
        for (let i = n - 1; i > 0; i--) {
            yield* swap(a, 0, i, c);
            c.sorted[i] = 1;
            yield* heapify(i, 0);
        }
        if (n > 0) c.sorted[0] = 1;
    }

    // In-place 3-way partition (handles duplicates like your
    // list-based quick_sort, which groups all values == pivot).
    function* quick(a, c) {
        function* qs(lo, hi) {
            if (lo > hi) return;
            if (lo === hi) { c.sorted[lo] = 1; return; }

            const p = a[(lo + hi) >> 1];
            let lt = lo, i = lo, gt = hi;
            while (i <= gt) {
                c.cmp++; c.hl = { cmp: [i], zone: [lt, gt] }; yield;
                if (a[i] < p) {
                    if (lt !== i) yield* swap(a, lt, i, c);
                    lt++; i++;
                } else if (a[i] > p) {
                    if (i !== gt) yield* swap(a, i, gt, c);
                    gt--;
                } else {
                    i++;
                }
            }
            for (let k = lt; k <= gt; k++) c.sorted[k] = 1;
            yield* qs(lo, lt - 1);
            yield* qs(gt + 1, hi);
        }
        yield* qs(0, a.length - 1);
    }

    const ALGORITHMS = {
        Bubble:    { fn: bubble,    best: "O(n)",       avg: "O(n²)" },
        Selection: { fn: selection, best: "O(n²)",      avg: "O(n²)" },
        Insertion: { fn: insertion, best: "O(n)",       avg: "O(n²)" },
        Merge:     { fn: merge,     best: "O(n log n)", avg: "O(n log n)" },
        Heap:      { fn: heap,      best: "O(n log n)", avg: "O(n log n)" },
        Quick:     { fn: quick,     best: "O(n log n)", avg: "O(n log n)" }
    };

    // ------------------------------------------------------
    // Runner (one per algorithm)
    // ------------------------------------------------------

    function makeRunner(name, input) {
        const a = input.slice();
        const c = {
            cmp: 0, wr: 0, steps: 0,
            hl: {}, sorted: new Uint8Array(a.length)
        };
        return {
            name, a, c,
            gen: ALGORITHMS[name].fn(a, c),
            done: false,
            rank: null,
            sweep: -1                         // finishing green sweep
        };
    }

    function advance(r) {
        if (r.done) return;
        const res = r.gen.next();
        if (res.done) {
            r.done = true;
            r.c.hl = {};
            r.sweep = 0;
        } else {
            r.c.steps++;
        }
    }

    // ------------------------------------------------------
    // Drawing
    // ------------------------------------------------------

    const COLORS = {
        base: "#2563eb", sorted: "#16a34a", cmp: "#f59e0b",
        write: "#ef4444", zone: "#a78bfa", pivot: "#7c3aed"
    };

    function draw(canvas, r, min, max) {
        const dpr = window.devicePixelRatio || 1;
        const w = canvas.clientWidth, h = canvas.clientHeight;
        if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
            canvas.width = w * dpr; canvas.height = h * dpr;
        }
        const ctx = canvas.getContext("2d");
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, w, h);

        const n = r.a.length;
        if (!n) return;
        const gap = n > 120 ? 0 : (n > 60 ? 1 : 2);
        const bw = (w - gap * (n - 1)) / n;
        const labelH = n <= 20 ? 14 : 0;
        const usable = h - labelH - 4;
        const hl = r.c.hl;
        const inList = (list, i) => list && list.indexOf(i) !== -1;
        const span = max - min;

        ctx.font = "bold 11px Arial";
        ctx.textAlign = "center";

        for (let i = 0; i < n; i++) {
            const v = r.a[i];
            const bh = 0.08 * usable + (span ? ((v - min) / span) * 0.92 * usable : 0.5 * usable);
            const x = i * (bw + gap);
            const y = h - bh - labelH;

            let col = COLORS.base;
            if (r.c.sorted[i] || (r.done && i <= r.sweep)) col = COLORS.sorted;
            if (hl.zone && i >= hl.zone[0] && i <= hl.zone[1] && !r.c.sorted[i]) col = COLORS.zone;
            if (inList(hl.pivot, i)) col = COLORS.pivot;
            if (inList(hl.cmp, i)) col = COLORS.cmp;
            if (inList(hl.write, i)) col = COLORS.write;

            ctx.fillStyle = col;
            ctx.fillRect(x, y, Math.max(bw, 0.6), bh);

            if (labelH) {
                ctx.fillStyle = "#475569";
                ctx.fillText(String(v), x + bw / 2, h - 2);
            }
        }
    }

    // ------------------------------------------------------
    // Page controller
    // ------------------------------------------------------

    function init(cfg) {
        const input = cfg.input;
        const min = Math.min.apply(null, input);
        const max = Math.max.apply(null, input);
        const grid = document.getElementById("viz-grid");
        const names = Object.keys(ALGORITHMS);

        const playBtn = document.getElementById("viz-play");
        const stepBtn = document.getElementById("viz-step");
        const resetBtn = document.getElementById("viz-reset");
        const speed = document.getElementById("viz-speed");
        const speedLabel = document.getElementById("viz-speed-label");
        const status = document.getElementById("viz-status");

        let runners = [], panels = {}, playing = false;
        let finished = 0, tick = 0, acc = 0, last = 0, dirty = true;

        // ops per second from slider 0..100  ->  1 .. ~8000
        const opsFromSlider = v => Math.pow(2, (v / 100) * 13);
        const sliderFromOps = o => Math.round(Math.log2(o) / 13 * 100);

        const n = input.length;
        const defaultOps = n <= 12 ? 6 : n <= 30 ? 30 : n <= 100 ? 150 : n <= 250 ? 800 : 3000;
        speed.value = sliderFromOps(defaultOps);

        function build() {
            grid.innerHTML = "";
            panels = {};
            names.forEach(name => {
                const info = ALGORITHMS[name];
                const tags = [];
                if (name === cfg.bestPredicted) tags.push('<span class="viz-tag ml">ML PICK</span>');
                if (name === cfg.bestActual) tags.push('<span class="viz-tag actual">FASTEST (ACTUAL)</span>');

                const el = document.createElement("div");
                el.className = "viz-panel" + (name === cfg.bestPredicted ? " recommended" : "");
                el.innerHTML =
                    '<div class="viz-head">' +
                        '<div><strong>' + name + ' Sort</strong>' +
                        '<div class="viz-complex">best ' + info.best + ' · avg ' + info.avg + '</div></div>' +
                        '<div class="viz-tags">' + tags.join("") + '</div>' +
                    '</div>' +
                    '<canvas class="viz-canvas"></canvas>' +
                    '<div class="viz-counters">' +
                        '<span>Compares <b data-k="cmp">0</b></span>' +
                        '<span>Writes <b data-k="wr">0</b></span>' +
                        '<span>Steps <b data-k="steps">0</b></span>' +
                    '</div>' +
                    '<div class="viz-finish" data-k="finish"></div>';
                grid.appendChild(el);
                panels[name] = {
                    el,
                    canvas: el.querySelector("canvas"),
                    cmp: el.querySelector('[data-k="cmp"]'),
                    wr: el.querySelector('[data-k="wr"]'),
                    steps: el.querySelector('[data-k="steps"]'),
                    finish: el.querySelector('[data-k="finish"]')
                };
            });
        }

        function reset(autoplay) {
            runners = names.map(nm => makeRunner(nm, input));
            finished = 0; tick = 0; acc = 0; dirty = true;
            names.forEach(nm => {
                panels[nm].finish.textContent = "";
                panels[nm].el.classList.remove("done");
            });
            setPlaying(!!autoplay);
            updateStatus();
            render();
        }

        function setPlaying(p) {
            playing = p;
            playBtn.textContent = p ? "⏸ Pause" : (finished === runners.length ? "↻ Replay" : "▶ Play");
        }

        function updateStatus() {
            status.textContent = finished === runners.length
                ? "All algorithms finished — " + tick + " steps for the slowest."
                : "Step " + tick + " · " + finished + " / " + runners.length + " finished";
        }

        function stepAll() {
            tick++;
            runners.forEach(r => {
                if (r.done) {
                    if (r.sweep >= 0 && r.sweep < r.a.length) r.sweep = Math.min(r.a.length, r.sweep + Math.max(1, Math.ceil(r.a.length / 40)));
                    return;
                }
                advance(r);
                if (r.done) {
                    finished++;
                    r.rank = finished;
                    const p = panels[r.name];
                    p.el.classList.add("done");
                    const medal = r.rank === 1 ? "🥇" : r.rank === 2 ? "🥈" : r.rank === 3 ? "🥉" : "🏁";
                    p.finish.textContent = medal + " Finished #" + r.rank + " in " + r.c.steps + " steps";
                }
            });
            dirty = true;
        }

        function allSettled() {
            return finished === runners.length &&
                runners.every(r => r.sweep >= r.a.length);
        }

        function render() {
            runners.forEach(r => {
                const p = panels[r.name];
                draw(p.canvas, r, min, max);
                p.cmp.textContent = r.c.cmp;
                p.wr.textContent = r.c.wr;
                p.steps.textContent = r.c.steps;
            });
            updateStatus();
            dirty = false;
        }

        function loop(ts) {
            if (playing) {
                if (!last) last = ts;
                acc += (ts - last) / 1000 * opsFromSlider(+speed.value);
                let guard = 0;
                while (acc >= 1 && guard < 4000) {
                    stepAll(); acc -= 1; guard++;
                    if (allSettled()) break;
                }
                if (allSettled()) setPlaying(false);
            }
            last = ts;
            if (dirty) render();
            requestAnimationFrame(loop);
        }

        playBtn.onclick = function () {
            if (finished === runners.length && allSettled()) { reset(true); return; }
            setPlaying(!playing);
        };
        stepBtn.onclick = function () { setPlaying(false); stepAll(); render(); };
        resetBtn.onclick = function () { reset(false); };
        speed.oninput = function () {
            speedLabel.textContent = Math.round(opsFromSlider(+speed.value)) + " steps/s";
        };
        window.addEventListener("resize", function () { dirty = true; });

        speed.oninput();
        build();
        reset(true);                       // autoplay as soon as results load
        requestAnimationFrame(loop);
    }

    root.SortingViz = { init, ALGORITHMS, makeRunner, advance };
    if (typeof module !== "undefined") module.exports = root.SortingViz;

})(typeof window !== "undefined" ? window : globalThis);
