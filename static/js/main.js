document.addEventListener("DOMContentLoaded", () => {
  // 1. Navigation & View Toggling
  const navToggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".links");
  if (navToggle && links) {
    navToggle.addEventListener("click", () =>
      links.classList.toggle("show-links"),
    );
  }

  const dropDownBtn = document.querySelector(".Drop_down_btn");
  const miniPlayerCloseBtn = document.querySelector(
    ".while_searching_play_close_btn",
  );
  const miniPlayerExpandBtn = document.querySelector(".mini_expand_btn");
  const body = document.body;

  if (dropDownBtn) {
    dropDownBtn.addEventListener("click", () =>
      body.classList.add("search-mode"),
    );
  }
  if (miniPlayerCloseBtn) {
    miniPlayerCloseBtn.addEventListener("click", () =>
      body.classList.remove("search-mode"),
    );
  }
  if (miniPlayerExpandBtn) {
    miniPlayerExpandBtn.addEventListener("click", () =>
      body.classList.remove("search-mode"),
    );
  }

  // 2. Fullscreen Logic
  const fullscreenBtn = document.querySelector(".fullscreen-btn");
  const playerContainer = document.querySelector(".player");
  const fullscreenIcon = fullscreenBtn
    ? fullscreenBtn.querySelector("i")
    : null;

  if (fullscreenBtn && playerContainer) {
    fullscreenBtn.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        playerContainer.requestFullscreen?.() ||
          playerContainer.webkitRequestFullscreen?.();
      } else {
        document.exitFullscreen?.() || document.webkitExitFullscreen?.();
      }
    });

    const updateFullscreenIcon = () => {
      if (fullscreenIcon) {
        const isFullscreen =
          document.fullscreenElement || document.webkitFullscreenElement;
        fullscreenIcon.classList.toggle("fa-expand", !isFullscreen);
        fullscreenIcon.classList.toggle("fa-compress", isFullscreen);
      }
    };
    document.addEventListener("fullscreenchange", updateFullscreenIcon);
    document.addEventListener("webkitfullscreenchange", updateFullscreenIcon);
  }

  // 3. Media Player Controls (Play/Pause, Skip, Progress Bar, Timer, Volume)
  const playPauseBtn = document.querySelector(".play_pause");
  const playPauseIcon = playPauseBtn ? playPauseBtn.querySelector("i") : null;
  const forwardBtn = document.querySelector(".Forward");
  const backwardBtn = document.querySelector(".Backward");

  const progressBar =
    document.querySelector(".progress-bar") ||
    document.querySelector("input[type='range']"); // Adjust selector if needed
  const currentTimeElem = document.querySelector(".current-time");
  const durationElem = document.querySelector(".total-duration");

  const volumeBtn = document.querySelector(".volume-btn");
  const volumeSlider = document.querySelector(".volume-slider");

  // Helper to get active media element
  const getActiveMedia = () => {
    const videoElement = document.querySelector(".player-video");
    const audioElement = document.querySelector(".player-audio");
    const videoSrc = videoElement
      ? videoElement.src || videoElement.querySelector("source")?.src
      : "";
    return videoElement && videoSrc && videoSrc !== window.location.href
      ? videoElement
      : audioElement;
  };

  // Format seconds into MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  // Play/Pause Button Logic
  if (playPauseBtn) {
    playPauseBtn.addEventListener("click", () => {
      const activeMedia = getActiveMedia();
      const activeSrc = activeMedia
        ? activeMedia.src || activeMedia.querySelector("source")?.src
        : "";

      if (!activeMedia || !activeSrc || activeSrc === window.location.href) {
        console.warn("No media source loaded yet!");
        alert("Please load an audio or video file first!");
        return;
      }

      if (activeMedia.paused) {
        activeMedia
          .play()
          .then(
            () =>
              playPauseIcon && (playPauseIcon.className = "fa-solid fa-pause"),
          )
          .catch((err) => console.error("Playback failed:", err));
      } else {
        activeMedia.pause();
        playPauseIcon && (playPauseIcon.className = "icon-Play-btn-1");
      }
    });
  }

  const updatePlayPauseIcon = () => {
    const activeMedia = getActiveMedia();

    if (!activeMedia || !playPauseIcon) return;

    if (activeMedia.paused) {
      playPauseIcon.className = "icon-Play-btn-1";
    } else {
      playPauseIcon.className = "fa-solid fa-pause";
    }
  };

  const activeMedia = getActiveMedia();

  if (activeMedia) {
    activeMedia.addEventListener("play", updatePlayPauseIcon);
    activeMedia.addEventListener("pause", updatePlayPauseIcon);
    activeMedia.addEventListener("ended", updatePlayPauseIcon);
  }

  // Skip Forward / Backward Logic (10 seconds)
  if (forwardBtn) {
    forwardBtn.addEventListener("click", () => {
      const activeMedia = getActiveMedia();
      if (activeMedia)
        activeMedia.currentTime = Math.min(
          activeMedia.duration || 0,
          activeMedia.currentTime + 10,
        );
    });
  }

  if (backwardBtn) {
    backwardBtn.addEventListener("click", () => {
      const activeMedia = getActiveMedia();
      if (activeMedia)
        activeMedia.currentTime = Math.max(0, activeMedia.currentTime - 10);
    });
  }

  // Track Progress & Update Timers continuously
  setInterval(() => {
    const activeMedia = getActiveMedia();
    if (!activeMedia || isNaN(activeMedia.duration)) return;

    // Update time displays
    if (currentTimeElem)
      currentTimeElem.textContent = formatTime(activeMedia.currentTime);
    if (durationElem)
      durationElem.textContent = formatTime(activeMedia.duration);

    // Update progress bar fill value if it's a range input
    if (progressBar && document.activeElement !== progressBar) {
      progressBar.max = activeMedia.duration;
      progressBar.value = activeMedia.currentTime;
    }
  }, 500);

  // Interactive Progress Bar Scrubbing
  if (progressBar) {
    progressBar.addEventListener("input", () => {
      const activeMedia = getActiveMedia();
      if (activeMedia && !isNaN(activeMedia.duration)) {
        activeMedia.currentTime = progressBar.value;
      }
    });
  }

  // Volume Controller Logic
  if (volumeSlider) {
    volumeSlider.addEventListener("input", (e) => {
      const activeMedia = getActiveMedia();
      if (activeMedia) {
        activeMedia.volume = e.target.value;
        activeMedia.muted = e.target.value == 0;
      }
    });
  }

  if (volumeBtn) {
    volumeBtn.addEventListener("click", () => {
      const activeMedia = getActiveMedia();
      if (activeMedia) {
        activeMedia.muted = !activeMedia.muted;
        if (volumeSlider)
          volumeSlider.value = activeMedia.muted ? 0 : activeMedia.volume;
      }
    });
  }
});

// Automatically hide or show the media poster based on active media type
const videoElement = document.querySelector(".player-video");
const mediaPoster = document.querySelector(".media-poster");

const videoSrc = videoElement
  ? videoElement.src || videoElement.querySelector("source")?.src
  : "";

if (mediaPoster) {
  if (videoElement && videoSrc && videoSrc !== window.location.href) {
    // If a video source exists, hide the audio poster so the video shows through
    mediaPoster.style.display = "none";
  } else {
    // Otherwise, show the poster for audio
    mediaPoster.style.display = "flex";
  }
}

// Ensure media is unmuted and at full volume on load
const activeVideo = document.querySelector(".player-video");
const activeAudio = document.querySelector(".player-audio");

[activeVideo, activeAudio].forEach((media) => {
  if (media) {
    media.muted = false;
    media.volume = 1.0;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.querySelector(".menu-toggle-btn");
  const closeBtn = document.querySelector(".close-nav-btn");
  const sideNavbar = document.querySelector(".side-navbar");
  const navOverlay = document.querySelector(".nav-overlay");

  function toggleMenu() {
    sideNavbar.classList.toggle("open");
    navOverlay.classList.toggle("active");
  }

  if (menuBtn) menuBtn.addEventListener("click", toggleMenu);
  if (closeBtn) closeBtn.addEventListener("click", toggleMenu);
  if (navOverlay) navOverlay.addEventListener("click", toggleMenu);
});

document.addEventListener("DOMContentLoaded", () => {
  // Selectors for full player and mini player elements
  const mainVideo =
    document.querySelector(".player video") ||
    document.querySelector(".player audio");
  const miniVideo =
    document.querySelector(".mini_media_container video") ||
    document.querySelector(".mini_media_container audio");

  const dropDownBtn = document.querySelector(".Drop_down_btn");
  const miniPlayerContainer = document.querySelector(
    ".playing_media_while_searching",
  );
  const expandBtn = document.querySelector(".mini_expand_btn");
  const closeMiniBtn = document.querySelector(
    ".while_searching_play_close_btn",
  );

  // 1. Minimize / Drop Down: Move from Full Player to Floating Mini Player
  if (dropDownBtn && miniPlayerContainer && mainVideo && miniVideo) {
    dropDownBtn.addEventListener("click", () => {
      // Sync the source if it differs
      if (miniVideo.src !== mainVideo.src) {
        miniVideo.src = mainVideo.src;
      }

      // Sync current timestamp and play state seamlessly
      miniVideo.currentTime = mainVideo.currentTime;

      if (!mainVideo.paused) {
        miniVideo
          .play()
          .catch((e) => console.log("Autoplay blocked by browser:", e));
        mainVideo.pause(); // Pause main so audio doesn't double up
      }

      // Reveal the mini player card at the bottom
      miniPlayerContainer.classList.remove("hidden");
    });
  }

  // 2. Expand or Close Mini Player: Return from Mini Player back to Full View
  const restoreFullPlayer = () => {
    if (mainVideo && miniVideo) {
      mainVideo.src = miniVideo.src;
      mainVideo.currentTime = miniVideo.currentTime;

      if (!miniVideo.paused) {
        mainVideo
          .play()
          .catch((e) => console.log("Autoplay blocked by browser:", e));
        miniVideo.pause();
      }

      // Hide the floating mini player card
      if (miniPlayerContainer) {
        miniPlayerContainer.classList.add("hidden");
      }
    }
  };

  if (expandBtn) expandBtn.addEventListener("click", restoreFullPlayer);
  if (closeMiniBtn) closeMiniBtn.addEventListener("click", restoreFullPlayer);
});

const mediaCards = document.querySelectorAll(".to_be_played_media");
mediaCards.forEach((card) => {
  card.addEventListener("click", () => {
    const selectedVideo = card.dataset.video;
    const playerVideo = document.querySelector(".player-video");

    playerVideo.src = selectedVideo;
    playerVideo.play();
    console.log("Selected video:", selectedVideo);
  });
});
