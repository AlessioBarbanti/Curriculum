%% cv.cls -- one-page, ATS-friendly CV class (pdfLaTeX).
%%
%% Derived from altacv.cls by LianTze Lim (https://github.com/liantze/AltaCV),
%% by way of techResume by Alex Calabrese (https://github.com/alexcalabrese/techResume).
%% This is a modified version: it is NOT the original AltaCV.
%%
%% Changes in this version (2026):
%%   - ligatures disabled and icons given an empty ActualText, so that text
%%     extractors (ATS) read clean words;
%%   - left/right rows built with \cvrow, so overlapping text is reported as
%%     "Overfull \hbox" instead of being hidden;
%%   - unused macros, packages and dead code removed.
%%
%% This work may be distributed and/or modified under the conditions of the
%% LaTeX Project Public License, either version 1.3c of this license or (at
%% your option) any later version. The latest version of this license is in
%%   https://www.latex-project.org/lppl.txt
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cv}[2026/10/11 One-page CV class derived from AltaCV]

\newif\if@raggedtwoe
\DeclareOption{ragged2e}{\@raggedtwoetrue}
\newif\if@withhyper
\DeclareOption{withhyper}{\@withhypertrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{extarticle}}
\ProcessOptions\relax
\LoadClass{extarticle}

\RequirePackage{etoolbox}
\RequirePackage[a-1b]{pdfx}
\RequirePackage{accsupp}
\RequirePackage[margin=2cm]{geometry}
\RequirePackage{xparse}
\RequirePackage{xcolor}
\RequirePackage{tikz}

%% Text layer: what an ATS reads must match what is printed.
\RequirePackage{cmap}
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\input{glyphtounicode}
\pdfgentounicode=1
\RequirePackage{microtype}
\DisableLigatures{encoding=*, family=*} % "fi" stays "f"+"i", not the single glyph U+FB01

%% Icons are decoration: give them an empty ActualText, otherwise \faCalendar is extracted as "z".
\RequirePackage[fixed]{fontawesome5}
\ExplSyntaxOn
\cs_set_eq:NN \__cv_fa_use_icon:nn \fontawesome_use_icon:nn
\cs_set_protected:Npn \fontawesome_use_icon:nn #1#2
  { \BeginAccSupp{method=plain,ActualText={}} \__cv_fa_use_icon:nn {#1}{#2} \EndAccSupp{} }
\ExplSyntaxOff

\if@raggedtwoe
  \RequirePackage[newcommands]{ragged2e}
\fi

\if@withhyper
  \AtBeginDocument{%
    \hypersetup{hidelinks}
    \urlstyle{same}
  }
\fi

\definecolor{NavyBlue}{HTML}{000080}
\definecolor{SlateGrey}{HTML}{2E2E2E}
\definecolor{LightGrey}{HTML}{666666}
\colorlet{name}{black}
\colorlet{heading}{NavyBlue}
\colorlet{headingrule}{NavyBlue}
\colorlet{accent}{NavyBlue}
\colorlet{emphasis}{SlateGrey}
\colorlet{body}{LightGrey}

\setlength{\parindent}{0pt}

%% \detokenize breaks UTF-8 in pdfLaTeX; alternative from https://tex.stackexchange.com/a/530911/226
\newcommand{\utffriendlydetokenize}[1]{%
\scantokens{%
  \catcode`\_=12%
  \catcode`\&=12%
  \catcode`\$=12%
  \catcode`\#=12%
  \catcode`\~=12%
  {#1}%
}%
}

%% Contact fields: \printinfo{icon}{text}[link]
\ExplSyntaxOn
\NewDocumentCommand{\printinfo}{m m o}{%
  \IfNoValueTF{#3}{%
    \mbox{\textcolor{accent}{\normalfont #1}~\utffriendlydetokenize{#2}\hspace{2em}}%
  }{%
    \if@withhyper%
      \mbox{\textcolor{accent}{\normalfont #1}~
      \href{#3}{\utffriendlydetokenize{#2}}\hspace{2em}}
    \else%
      \mbox{\textcolor{accent}{\normalfont #1}~{\utffriendlydetokenize{#3#2}}\hspace{2em}}%
    \fi%
  }%
}%

%% \NewInfoField{command}{icon}[link prefix] defines \command{text}
\NewDocumentCommand{\NewInfoField}{m m o}{%
  \IfNoValueF{#3}{\csdef{#1 hyperprefix}{#3}}%
  \csdef{#1 symbol}{#2}%
  \csdef{#1}##1{%
    \if@withhyper
      \IfNoValueTF {#3}
        {\printinfo{\csuse{#1 symbol}}{##1}}%
        {\printinfo{\csuse{#1 symbol}}{##1}[\csuse{#1 hyperprefix}##1]}%
    \else
      \printinfo{\csuse{#1 symbol}}{##1}%
    \fi%
  }%
}
\ExplSyntaxOff

\NewInfoField{email}{\faEnvelope}[mailto:]
\NewInfoField{github}{\faGithub}[https://github.com/]
\NewInfoField{linkedin}{\faLinkedin}[https://linkedin.com/in/]
\NewInfoField{location}{\faMapMarker}

\newcommand{\name}[1]{\def\@name{#1}}
\newcommand{\namefont}{\Huge\bfseries}
\newcommand{\cvsectionfont}{\large\bfseries}

\newcommand{\makecvheader}{%
  {\centering\namefont\color{name}\MakeUppercase{\@name}\par}
  \medskip\medskip\medskip
}

\newcommand{\cvsection}[1]{%
  \nointerlineskip\bigskip
  {\color{heading}\cvsectionfont\MakeUppercase{#1}}\\[-1ex]%
  {\color{headingrule}\rule{\linewidth}{1pt}\par}\medskip
}

%% A row with text on the left and on the right. If the two overlap or cross the
%% margin, TeX reports "Overfull \hbox" in the log (\makebox would hide it).
\newcommand{\cvrow}[2]{\par\noindent\hbox to\linewidth{{#1}\hfil\hskip1em{#2}}\par}

%% \cveducation{degree}{school}{date}{grade}
\newcommand{\cveducation}[4]{%
  \cvrow{\small\color{emphasis}\textbf{#1}}{\small\color{emphasis}\textbf{#2}}\smallskip
  \cvrow{\small\ifstrequal{#4}{}{}{\faClipboardCheck~#4}}{\small\ifstrequal{#3}{}{}{\faCalendar~#3}}
  \medskip\normalsize
}

%% \cvexperience{role}{company}{dates}{city}{tags} followed by the description
\newcommand{\cvexperience}[5]{%
  \cvrow{\small\color{emphasis}\textbf{#1}}{\small\color{emphasis} \textbf{#4}, #2}\smallskip
  \cvrow{\small#5}{\small\ifstrequal{#3}{}{}{\faCalendar~#3}}
  \medskip\normalsize
}

%% \cvproject{title}{subtitle}{tags}{link} followed by the description
\newcommand{\cvproject}[4]{%
  \cvrow{\small\color{emphasis}#1}{\small\color{emphasis}\textbf{#2}}\smallskip
  \cvrow{\footnotesize\ifstrequal{#3}{}{}{\faCode~#3}}{\small\ifstrequal{#4}{}{}{\faGithub #4}}
  \medskip\normalsize
}

\newcommand{\cvtag}[1]{%
  \tikz[baseline]\node[anchor=base,draw=body!30,rounded corners,inner xsep=1ex,inner ysep =0.75ex,text height=1.5ex,text depth=.25ex]{#1};
}

\AtBeginDocument{%
  \pagestyle{empty}
  \color{body}
  \raggedright
}
