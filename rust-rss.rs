use std::fs::{self, OpenOptions};
use std::io::{self, Write};
use chrono::{DateTime, Utc};
use pulldown_cmark::{html, Parser};
use std::env;

// Function to convert Markdown to HTML
fn markdown_to_html(markdown: &str) -> String {
    let parser = Parser::new(markdown);
    let mut html_output = String::new();
    html::push_html(&mut html_output, parser);
    html_output
}

fn main() {
    // Read command line arguments
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: <title> <contents>");
        return;
    }
    let title = &args[1];
    let contents = &args[2];

    // Format the date and time as required
    let now: DateTime<Utc> = Utc::now();
    let pub_date = now.format("%a, %d %b %Y %H:%M:%S GMT").to_string();

    // Combine title and date to create guid
    let date = now.format("%Y-%m-%d_%H:%M:%S").to_string();
    let stripped_title = title.replace(" ", "_");
    let guid = format!("{}_{}", stripped_title, date);

    // Convert Markdown contents to HTML
    let description = markdown_to_html(contents);

    // Print out the XML
    let new_entry_xml = format!(
        "        <item>\n            <title>{}</title>\n            <guid>{}</guid>\n            <pubDate>{}</pubDate>\n            <description><![CDATA[\n                {}            ]]></description>\n        </item>",
        title, guid, pub_date, description
    );
    println!("{}", new_entry_xml);
}
