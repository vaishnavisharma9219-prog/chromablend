/**
 * CHROMA BLEND — Hidden Long-Press Interaction
 * Discreet access trigger on the Chroma Blend logo/name.
 */

(function () {
  const HOLD_DURATION = 1700; // 1.7 seconds
  const MOVE_THRESHOLD = 8;   // 8 pixels movement tolerance

  let holdTimer = null;
  let progressInterval = null;
  let startTime = null;
  let startX = 0;
  let startY = 0;
  let isHolding = false;

  function initLongPress() {
    const trigger = document.getElementById('logo-trigger');
    const circle = document.getElementById('logo-progress-circle');
    const modal = document.getElementById('private-access-modal');
    const pinInput = document.getElementById('access-pin-input');
    const pinSubmit = document.getElementById('access-pin-submit');
    const pinCancel = document.getElementById('access-pin-cancel');
    const pinError = document.getElementById('access-pin-error');

    if (!trigger || !circle) return;

    const circumference = 88; // 2 * PI * r where r=14

    function resetProgress() {
      clearTimeout(holdTimer);
      clearInterval(progressInterval);
      circle.style.strokeDashoffset = circumference;
      isHolding = false;
      holdTimer = null;
      progressInterval = null;
    }

    function startHold(clientX, clientY) {
      startX = clientX;
      startY = clientY;
      isHolding = true;
      startTime = Date.now();

      // Progress animation loop
      progressInterval = setInterval(() => {
        if (!isHolding) return;
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / HOLD_DURATION, 1);
        const offset = circumference - (progress * circumference);
        circle.style.strokeDashoffset = offset;
      }, 30);

      holdTimer = setTimeout(() => {
        resetProgress();
        triggerAccessModal();
      }, HOLD_DURATION);
    }

    function checkMovement(clientX, clientY) {
      if (!isHolding) return;
      const dx = Math.abs(clientX - startX);
      const dy = Math.abs(clientY - startY);
      if (dx > MOVE_THRESHOLD || dy > MOVE_THRESHOLD) {
        resetProgress();
      }
    }

    // Mouse events
    trigger.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // Only primary click
      startHold(e.clientX, e.clientY);
    });

    window.addEventListener('mousemove', (e) => {
      checkMovement(e.clientX, e.clientY);
    });

    window.addEventListener('mouseup', () => {
      if (isHolding) resetProgress();
    });

    // Touch events
    trigger.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        startHold(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1) {
        checkMovement(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      if (isHolding) resetProgress();
    });

    window.addEventListener('touchcancel', () => {
      if (isHolding) resetProgress();
    });

    // Modal Interaction
    function triggerAccessModal() {
      if (!modal) return;
      modal.classList.add('active');
      if (pinError) pinError.style.display = 'none';
      if (pinInput) {
        pinInput.value = '';
        setTimeout(() => pinInput.focus(), 150);
      }
    }

    if (pinCancel) {
      pinCancel.addEventListener('click', () => {
        modal.classList.remove('active');
      });
    }

    async function submitPin() {
      if (!pinInput) return;
      const passcode = pinInput.value.trim();
      if (!passcode) return;

      if (pinError) pinError.style.display = 'none';
      if (pinSubmit) {
        pinSubmit.disabled = true;
        pinSubmit.textContent = 'Verifying...';
      }

      try {
        const res = await API.post('/private-access/verify', { passcode });
        if (res && res.data && res.data.unlocked) {
          modal.classList.remove('active');
          window.location.href = '/private.html';
        }
      } catch (err) {
        if (pinError) {
          pinError.textContent = 'Access code not recognized.';
          pinError.style.display = 'block';
        }
        pinInput.value = '';
        pinInput.focus();
      } finally {
        if (pinSubmit) {
          pinSubmit.disabled = false;
          pinSubmit.textContent = 'Enter';
        }
      }
    }

    if (pinSubmit) {
      pinSubmit.addEventListener('click', submitPin);
    }

    if (pinInput) {
      pinInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          submitPin();
        } else if (e.key === 'Escape') {
          modal.classList.remove('active');
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', initLongPress);
})();
