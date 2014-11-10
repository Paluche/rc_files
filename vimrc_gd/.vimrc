"To remeber
"n/o/i/map = normal operating inserting mode map
"ioi/map to map a key
"ion/noremap is a no recursive command
"map j gg j=gg
"map G j q=j=gg
"noremap W j W=j!=gg

"******************************************************************************
" VUNDLE CONFIG
"******************************************************************************
set nocompatible               " be iMproved
filetype off                   " required!

set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

" let Vundle manage Vundle
" required! 
Bundle 'gmarik/vundle'
Bundle 'scrooloose/nerdtree'
Bundle 'Valloric/YouCompleteMe'
let g:ycm_global_ycm_extra_conf = "~/.vim/.ycm_extra_conf.py"

Bundle 'SirVer/ultisnips'
Bundle 'honza/vim-snippets'
"let g:UltiSnipsExpandTrigger="<tab>"
let g:UltiSnipsJumpForwardTrigger="<c-b>"
let g:UltiSnipsJumpBackwardTrigger="<c-z>"
let g:UltiSnipsSnippetDirectories=["UltiSnips"]

" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"

let g:UltiSnipsExpandTrigger = "<nop>"
let g:ulti_expand_or_jump_res = 0
function ExpandSnippetOrCarriageReturn()
    let snippet = UltiSnips#ExpandSnippetOrJump()
    if g:ulti_expand_or_jump_res > 0
        return snippet
    else
        return "\<CR>"
    endif
endfunction

inoremap <expr> <CR> pumvisible() ? "<C-R>=ExpandSnippetOrCarriageReturn()<CR>" : "\<CR>"

let g:NERDTreeWinSize=50

Bundle 'tikhomirov/vim-glsl'

"Bundle 'Rip-Rip/clang_complete'
"clang_complete configuration
"Clang autocomplete customization
"Complete options (disable preview scratch window)
set completeopt=menu,menuone,longest
"set completefunc=clang_complete
"Show clang errors in the quickfix window
"let g:clang_complete_copen=1
"let g:clang_auto_select=0
"let g:clang_snippets=1
"let g:clang_snippets_engine='clang_complete'
"let g:clang_user_options='-std=c++0x'
"let g:clang_periodic_quickfix=1
"let g:clang_complete_macros=1
"let g:clang_complete_patterns=1
"let g:clang_library_path='/usr/lib/llvm-3.4/lib/'
Bundle 'taglist.vim'
let Tlist_WinWidth=50
set tags=/home/gmichel/tags/camera
map <F3> <C-T>
map <F2> :call TagInNewTab()<CR>
map <F7> :!aspell -c %<CR>
Bundle 'nanotech/jellybeans.vim'
Bundle 'tomasr/molokai'

filetype plugin indent on     " required!
"
" Brief help
" :BundleList          - list configured bundles
" :BundleInstall(!)    - install(update) bundles
" :BundleSearch(!) foo - search(or refresh cache first) for foo
" :BundleClean(!)      - confirm(or auto-approve) removal of unused bundles
"
" see :h vundle for more details or wiki for FAQ
" NOTE: comments after Bundle command are not allowed..

"******************************************************************************
" VIM CONFIGURATION
"******************************************************************************
set expandtab          "When expandtab is set, hitting Tab in insert mode will produce the appropriate number of spaces. 
set shiftwidth=4       "Set shiftwidth to control how many columns text is indented with the reindent operations (<< and >>) and automatic C-style indentation. 
set tabstop=4          "Set tabstop to tell vim how many columns a tab counts for
set t_Co=256           "Number of colors for terminal
"set tw=80              "Text width in a file
set hls                "Enable hightlight search
if has("gui_running")
    set lines=200 columns=200
    hi Search guibg=peru guifg=wheat
    colorscheme desert "Set the molokai theme
else
    colorscheme jellybeans "Set the jellybeans theme
    hi Search cterm=NONE ctermfg=black ctermbg=yellow
endif
"#set background=dark
"colorscheme molokai "Set the molokai theme
set number             "Display line number
set pumheight=20       "Limit popup menu height
"set mouse=a            "Enable the mouse on vim

set gfn=DejaVu\ Sans\ Mono\ 9 "This is for GVIM
"set smarttab ???
"set lbr
"set ai                "Auto indent
"set si                "Smart indet
"set wrap              "Wrap lines
set clipboard=unnamedplus

set guioptions+=m  "remove menu bar
set guioptions+=T  "remove toolbar
"set guioptions-=r  "remove right-hand scroll bar
"set guioptions-=L  "remove right-hand scroll bar
set colorcolumn=80

" Put all backup and swap files in .vim directory
" The double tailing slash will store files using full paths so if you edit
" two different models.py files you won't clobber your swap or backups.
set backupdir=~/.vim/backup//
set directory=~/.vim/swp//

"map is recursive key mapping
"noremap is non recursive key mapping version
"ion ar the modes Insert Operator Normal for example

au BufNewFile,BufRead *.frag,*.vert,*.fp,*.vp,*.glsl,*.vsh,*.fsh setf glsl

"******************************************************************************
" KEY BINDINGS
"******************************************************************************
"Remap some commands key
map <PageUp> 10k
map <PageDown> 10j
map <C-n> :Texplore<CR>
map <C-left> :tabprevious<CR>
map <C-right> :tabnext<CR>
map <F12> :q!<CR>
"c-@ = C-Space
imap <C-Space> <C-x><C-u>
imap <C-@> <C-x><C-u>

nmap <F5> :NERDTreeToggle<CR>
nmap <F6> :TlistToggle<CR>
set makeprg=/home/gmichel/SVN/system/Camera/build/build.sh
nmap <F12> :cd /home/gmichel/SVN/system/Camera/build<CR>:copen<CR>:make -t camera-dev -n <CR>:cd - <CR>
nmap <F10> :cnext<CR>
nmap <F11> :cprevious<CR>

set pastetoggle=<F9>
set modeline
set ls=2

"******************************************************************************
" TAB FORMAT
"******************************************************************************
set guitablabel=\[%N\]\ %t\ %M 
set tabline=%!MyTabLine()

function! TagInNewTab()
    let word = expand("<cword>")
    redir => tagsfiles
    silent execute 'set tags'
    redir END
    tabe
    execute 'setlocal' . strpart(tagsfiles, 2)
    execute 'tag ' . word
endfunction

function MyTabLine()
    let s = ''
    for i in range(tabpagenr('$'))
        " select the highlighting
        if i + 1 == tabpagenr()
        let s .= '%#TabLineSel#'
        else
        let s .= '%#TabLine#'
        endif
        " set the tab page number (for mouse clicks)
        let s .= '%' . (i + 1) . 'T'
        " the label is made by MyTabLabel()
        let s .= ' %{MyTabLabel(' . (i + 1) . ')} '
    endfor
    " after the last tab fill with TabLineFill and reset tab page nr
    let s .= '%#TabLineFill#%T'
    " right-align the label to close the current tab page
    if tabpagenr('$') > 1
    let s .= '%=%#TabLine#%999Xclose'
    endif
    return s
endfunction

function MyTabLabel(n)
    let buflist = tabpagebuflist(a:n)
    let winnr   = tabpagewinnr(a:n)
    let bufnam  = bufname(buflist[winnr - 1])
    " This is getting the basename() of bufname above
    let base    = substitute(bufnam, '.*/', '', '')
    let modif   = getbufvar(buflist[winnr - 1], "&mod")?'[+] ':''
    let name    = a:n . ' ' . modif . base
    return name
endfunction
