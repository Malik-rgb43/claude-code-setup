# פתרון בעיות

<!-- step: trouble-01 -->
## trouble-01 - `claude` לא נמצא
מתקינים את Claude Code מ-https://code.claude.com/docs/en/overview, פותחים טרמינל **חדש** ומריצים שוב את התוכנית.

<!-- step: trouble-02 -->
## trouble-02 - Python לא נמצא, או שנפתחת חנות Microsoft
ב-Windows ה-`python` יכול להיות קיצור לחנות (קוד יציאה 9009). מנסים `py -3 --version`. מתקינים Python 3.12 מ-python.org או `winget install --id Python.Python.3.12 -e --source winget`, ופותחים טרמינל חדש.

<!-- step: trouble-03 -->
## trouble-03 - Playwright חסום: חסר Node
מתקינים Node LTS (`winget install --id OpenJS.NodeJS.LTS -e --source winget` ב-Windows, `brew install node` ב-macOS), פותחים טרמינל **חדש** ומריצים שוב `apply`. המתקין אף פעם לא מתקין Node בשבילך.

<!-- step: trouble-04 -->
## trouble-04 - Superpowers חסום או נכשל
חייב להיות מותקן Git (תוספים נמשכים מ-GitHub). אם שורת הכישלון מזכירה את הרשת, בודקים את החיבור ומריצים שוב `apply`. אפשר גם להוסיף ידנית בתוך Claude Code: `/plugin install superpowers@claude-plugins-official`.

<!-- step: trouble-05 -->
## trouble-05 - התוסף או השרת לא מופיעים
מפעילים מחדש את Claude Code (סוגרים ומריצים `claude` שוב): תוספים ושרתים נקראים בהפעלה. אחר כך `claude plugin list` ו-`claude mcp get playwright`. מריצים `python install/setup.py verify`.

<!-- step: trouble-06 -->
## trouble-06 - אני רוצה שלדפדפן יהיה חלון
מריצים `claude mcp remove playwright --scope user`, ואז `claude mcp add --scope user --transport stdio playwright -- npx @playwright/mcp@0.0.83 --isolated` (ב-Windows: `cmd /c npx ...`). שים לב: אחרי זה `uninstall` כבר לא יתייחס לשרת כאל שרת שהוא הוסיף.

<!-- step: trouble-07 -->
## trouble-07 - ה-CLAUDE.md שלי נראה אחרת
הבלוק נמצא בין `<!-- avc-claude-code-setup:begin v1 -->` לבין `<!-- avc-claude-code-setup:end -->`. כל מה שמחוץ לסימונים הוא שלך. גיבוי של הקובץ מלפני השינוי הראשון נמצא ב-`~/.avc/claude-code-setup/backups/`.
