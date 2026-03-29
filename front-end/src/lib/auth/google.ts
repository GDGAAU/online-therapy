import { browser } from "$app/environment";

declare global {
  interface GooglePromptMomentNotification {
    isNotDisplayed: () => boolean;
    isSkippedMoment: () => boolean;
    isDismissedMoment: () => boolean;
    getNotDisplayedReason: () => string;
    getSkippedReason: () => string;
    getDismissedReason: () => string;
  }

  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential?: string }) => void;
          }) => void;
          prompt: (
            listener?: (notification: GooglePromptMomentNotification) => void,
          ) => void;
          cancel: () => void;
        };
      };
    };
  }
}

let googleScriptLoadingPromise: Promise<void> | null = null;

function loadGoogleScript(): Promise<void> {
  if (!browser)
    return Promise.reject(
      new Error("Google OAuth is only available in the browser."),
    );

  if (window.google?.accounts?.id) return Promise.resolve();

  if (googleScriptLoadingPromise) return googleScriptLoadingPromise;

  googleScriptLoadingPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector(
      'script[data-google-identity="true"]',
    ) as HTMLScriptElement | null;

    if (existing) {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener(
        "error",
        () => reject(new Error("Failed to load Google Identity script.")),
        {
          once: true,
        },
      );
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.dataset.googleIdentity = "true";
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Failed to load Google Identity script."));
    document.head.appendChild(script);
  });

  return googleScriptLoadingPromise;
}

export async function requestGoogleIdToken(clientId: string): Promise<string> {
  const normalizedClientId = clientId.trim();

  if (!normalizedClientId) {
    throw new Error("Missing Google client id.");
  }

  await loadGoogleScript();

  if (!window.google?.accounts?.id) {
    throw new Error("Google Identity API is unavailable.");
  }

  return new Promise<string>((resolve, reject) => {
    let completed = false;

    function fail(message: string) {
      if (completed) return;
      completed = true;
      window.clearTimeout(timeoutId);
      reject(new Error(message));
    }

    const timeoutId = window.setTimeout(() => {
      fail(
        "Google sign-in timed out. Check Google OAuth Authorized JavaScript origins and try again.",
      );
    }, 60000);

    window.google!.accounts.id.initialize({
      client_id: normalizedClientId,
      callback: (response) => {
        if (completed) return;
        completed = true;
        window.clearTimeout(timeoutId);

        const credential = response?.credential;
        if (!credential) {
          reject(
            new Error(
              "Google sign-in was cancelled or did not return a token.",
            ),
          );
          return;
        }

        resolve(credential);
      },
    });

    window.google!.accounts.id.cancel();
    window.google!.accounts.id.prompt((notification) => {
      if (completed) return;

      if (notification.isNotDisplayed()) {
        const reason = notification.getNotDisplayedReason?.() ?? "unknown";
        fail(
          `Google sign-in couldn't be displayed (${reason}). If this is local dev, confirm your origin is added to Google OAuth Authorized JavaScript origins.`,
        );
        return;
      }

      if (notification.isSkippedMoment()) {
        const reason = notification.getSkippedReason?.() ?? "unknown";
        fail(`Google sign-in was skipped (${reason}).`);
        return;
      }

      if (notification.isDismissedMoment()) {
        const reason = notification.getDismissedReason?.() ?? "unknown";
        fail(`Google sign-in was dismissed (${reason}).`);
      }
    });
  });
}
