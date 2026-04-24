/**
 * layout.js
 * 負責 IDE 的十字拖拉佈局與效能優化
 */
export function createLayoutModule({ editor, elements }) {
    const {
        splitH,
        splitVTop,
        splitVBottom,
        topRow,
        bottomRow,
        controlPanel,
        logsPanel,
        editorPanel,
        terminalPanel
    } = elements;

    let currentResizer = null;
    let rafId = null;

    // 防止面板被拉到 0% 或 100% 導致無法拉回
    const clamp = (v, min, max) => Math.min(Math.max(v, min), max);

    const onMouseDown = (e) => {
        currentResizer = e.target;
        document.body.classList.add('no-select');
    };

    const updateLayout = (e) => {
        if (!currentResizer) return;

        if (currentResizer === splitH) {
            // 上下拖拉
            let h = (e.clientY / window.innerHeight) * 100;
            h = clamp(h, 10, 90);
            topRow.style.height = `${h}%`;
            bottomRow.style.height = `${100 - h}%`;
        } else {
            // 左右拖拉
            let w = (e.clientX / window.innerWidth) * 100;
            w = clamp(w, 10, 90);

            if (currentResizer === splitVTop) {
                controlPanel.style.width = `${w}%`;
                logsPanel.style.width = `${100 - w}%`;
            } else if (currentResizer === splitVBottom) {
                editorPanel.style.width = `${w}%`;
                terminalPanel.style.width = `${100 - w}%`;
            }
        }

        // 🌟 拖拉時即時通知 CodeMirror 重新計算寬高，防止黑塊
        if (editor) {
            editor.refresh();
        }
    };

    const onMouseMove = (e) => {
        if (!currentResizer) return;

        // 使用 RAF 進行效能優化，確保每秒 60 幀流暢度
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => updateLayout(e));
    };

    const onMouseUp = () => {
        currentResizer = null;
        document.body.classList.remove('no-select');
        if (rafId) cancelAnimationFrame(rafId);
    };

    // 綁定事件監聽
    [splitH, splitVTop, splitVBottom].forEach(s =>
        s?.addEventListener('mousedown', onMouseDown)
    );

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    // 暴露 destroy 方法供外部進行清理，防止記憶體洩漏
    return {
        destroy() {
            [splitH, splitVTop, splitVBottom].forEach(s =>
                s?.removeEventListener('mousedown', onMouseDown)
            );
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            if (rafId) cancelAnimationFrame(rafId);
        }
    };
}
