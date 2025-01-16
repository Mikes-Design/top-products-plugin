
<?php
/*
Plugin Name: Top Products Plugin
Description: Automatically fetch and display top products by category.
Version: 1.0
Author: Your Name
*/

function fetch_and_process_data() {
    // Run your Python script to fetch and process data
    shell_exec('python3 /path_to_your_project/top-products-plugin/scripts/fetch_top_products.py');
}

function scrape_and_update_data() {
    // Run your Scrapy spider to scrape the website
    shell_exec('scrapy runspider /path_to_your_project/top-products-plugin/scripts/mycrawler/mycrawler/spiders/myspider.py');
}

// Schedule the fetch_and_process_data function to run daily
if (!wp_next_scheduled('fetch_and_process_data_hook')) {
    wp_schedule_event(time(), 'daily', 'fetch_and_process_data_hook');
}
add_action('fetch_and_process_data_hook', 'fetch_and_process_data');

// Schedule the scrape_and_update_data function to run weekly
if (!wp_next_scheduled('scrape_and_update_data_hook')) {
    wp_schedule_event(time(), 'weekly', 'scrape_and_update_data_hook');
}
add_action('scrape_and_update_data_hook', 'scrape_and_update_data');

function display_top_products() {
    global $wpdb;
    $results = $wpdb->get_results("SELECT * FROM top_products ORDER BY category, reviews DESC");

    $output = '<div class="top-products">';
    foreach ($results as $product) {
        $output .= '<div class="product">';
        $output .= '<h2>' . esc_html($product->name) . '</h2>';
        $output .= '<p>' . esc_html($product->price) . '</p>';
        $output .= '<p>' . esc_html($product->reviews) . ' reviews</p>';
        $output .= '</div>';
    }
    $output .= '</div>';

    return $output;
}

add_shortcode('top_products', 'display_top_products');
?>
