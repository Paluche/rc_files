;; .emacs author : Alexis Polti
(put 'narrow-to-region 'disabled nil)

;;; Customizations go in .emacs.d
(add-to-list 'load-path "~/.emacs.d/")

;; ===== Set standard indent to 2
(setq standard-indent 2)
(setq default-tab-width 2)
(setq default-py-indent-offset 2)
(setq c-basic-offset 2)

;; ========== Line by line scrolling ==========
;; This makes the buffer scroll by only a single line when the up or
;; down cursor keys push the cursor (tool-bar-mode) outside the
;; buffer. The standard emacs behaviour is to reposition the cursor in
;; the center of the screen, but this can make the scrolling confusing
(setq scroll-step 1)

;; ========== Support Wheel Mouse Scrolling ==========
(mouse-wheel-mode t)

;; Tab using spaces
(setq-default indent-tabs-mode nil)

;; ========== Enable Line and Column Numbering ==========
;; Show line-number in the mode line
(line-number-mode 1)
;; Show column-number in the mode line
(column-number-mode 1)

;;; Better buffer switching
(iswitchb-mode 1)

;;; Use font-lock-mode
(global-font-lock-mode 1)

;; default to better frame titles
(setq frame-title-format (concat  "%b - emacs@" system-name))


(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(auto-save-file-name-transforms (quote ((".*" "~/.emacs.d/autosaves/\\1" t))))
 '(backup-directory-alist (quote ((".*" . "~/.emacs.d/backups/"))))
 '(column-number-mode t)
 '(indicate-empty-lines t)
 '(inhibit-startup-screen t)
 '(scroll-bar-mode (quote right))
 '(show-paren-mode t)
 '(size-indication-mode t)
 '(verilog-auto-newline nil))

; Load verilog mode only when needed
(autoload 'verilog-mode "verilog-mode" "Verilog mode" t )
; Load verilog mode also for .sv file (system verilog)
(setq auto-mode-alist (cons '("\\.sv\\'" . verilog-mode) auto-mode-alist))
; Any files in verilog mode should have their keywords colorized
(add-hook 'verilog-mode-hook '(lambda () (font-lock-mode 1)))

(if (fboundp 'pc-selection-mode)
    (pc-selection-mode)
  (require 'pc-select))
(custom-set-faces
  ;; custom-set-faces was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 98 :width normal :foundry "unknown" :family "DejaVu Sans Mono")))))

(put 'downcase-region 'disabled nil)

;; Open files and goto lines like we see from g++ etc. i.e. file:line#
;; (to-do "make `find-file-line-number' work for emacsclient as well")
;; (to-do "make `find-file-line-number' check if the file exists")
(defadvice find-file (around find-file-line-number
                             (filename &optional wildcards)
                             activate)
  "Turn files like file.cpp:14 into file.cpp and going to the 14-th line."
  (save-match-data
    (let* ((matched (string-match "^\\(.*\\):\\([0-9]+\\):?$" filename))
           (line-number (and matched
                             (match-string 2 filename)
                             (string-to-number (match-string 2 filename))))
           (filename (if matched (match-string 1 filename) filename)))
      ad-do-it
      (when line-number
        ;; goto-line is for interactive use
        (goto-char (point-min))
        (forward-line (1- line-number))))))


;; Put autosave files (ie #foo#) and backup files (ie foo~) in ~/.emacs.d/.


;; create the autosave dir if necessary, since emacs won't.
(make-directory "~/.emacs.d/autosaves/" t)

(setq version-control t ;; Use version numbers for backups
      kept-new-versions 16 ;; Number of newest versions to keep
      kept-old-versions 2 ;; Number of oldest versions to keep
      delete-old-versions t ;; Ask to delete excess backup versions?
      backup-by-copying-when-linked t) ;; Copy linked files, don't rename.

(defun force-backup-of-buffer ()
  (let ((buffer-backed-up nil))
    (backup-buffer)))

(add-hook 'before-save-hook  'force-backup-of-buffer)

;; cleanup on return
(add-hook 'before-save-hook 'delete-trailing-whitespace)

;; Python misc, as per http://pedrokroger.net/2010/07/configuring-emacs-as-a-python-ide-2/
(require 'lambda-mode)
(add-hook 'python-mode-hook #'lambda-mode 1)
(setq lambda-symbol (string (make-char 'greek-iso8859-7 107)))

;; ;; python-mode settings
(setq auto-mode-alist (cons '("\\.py$" . python-mode) auto-mode-alist))
(setq interpreter-mode-alist(cons '("python" . python-mode)
                             interpreter-mode-alist))
;; path to the python interpreter, e.g.: ~rw/python27/bin/python2.7
(setq py-python-command "python")
(autoload 'python-mode "python-mode" "Python editing mode." t)

