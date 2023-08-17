module RedditKit
    class Client < API
    
        # Methods for searching reddit's links.
        module Search
    
        # Search for links.
        #
        # @param query [String] The search query.
        # @option options [String, RedditKit::Subreddit] subreddit The optional subreddit to search.
        # @option options [true, false] restrict_to_subreddit Whether to search only in a specified subreddit.
        # @option options [1..100] limit The number of links to return.
        # @option options [String] count The number of results to return before or after. This is different from `limit`.
        # @option options [relevance, new, hot, top, comments] sort The sorting order for search results.
        # @option options [String] before Only return links before this full name.
        # @option options [String] after Only return links after this full name.
        # @option options [cloudsearch, lucene, plain] syntax Specify the syntax for the search. Learn more: http://www.reddit.com/r/redditdev/comments/1hpicu/whats_this_syntaxcloudsearch_do/cawm0fe
        # @option options [hour, day, week, month, year, all] time Show results with a specific time period.
        # @return [RedditKit::PaginatedResponse]
        def search(query, options = {})
            path = "%s/search.json" % ('r/' + options[:subreddit] if options[:subreddit])
            parameters = { :q => query,
                            :restrict_sr => options[:restrict_to_subreddit],
                            :limit       => options[:limit],
                            :count       => options[:count],
                            :sort        => options[:sort],
                            :before      => options[:before],
                            :after       => options[:after],
                            :syntax      => options[:syntax],
                            :t           => options[:time]
            }

            objects_from_response(:get, path, parameters)
        end

        def self.my_method(a)
            # Method implementation
            puts(a)
            return a
        end
    
    end
  end
end

load_current_value do |new_resource, old_resource|
    unless current_installed_version(new_resource).nil?
      version(current_installed_version(new_resource))
      Chef::Log.debug("Current version is #{version}") if version
      return a
    end
  end
  
  action :install  do
    build_essential
  
    install_version = new_resource.version unless new_resource.version.nil? || new_resource.version == current_resource.version
    versions_match = candidate_version == current_installed_version(new_resource)
  
    if install_version || new_resource.version.nil? && !versions_match
      converge_by("install package #{new_resource.package_name} #{install_version}") do
        info_output = "Installing #{new_resource.package_name}"
        info_output << " version #{install_version}" if install_version && !install_version.empty?
        Chef::Log.info(info_output)
        install_package(new_resource.package_name, install_version)
      end
    end
  end
  
  action :reinstall do
    build_essential
    
    install_version = new_resource.version unless new_resource.version.nil?
    converge_by("reinstall package #{new_resource.package_name} #{install_version}") do
      info_output = "Installing #{new_resource.package_name}"
      info_output << " version #{install_version}" if install_version && !install_version.empty?
      Chef::Log.info(info_output)
      install_package(new_resource.package_name, install_version, force: true)
    end
  end

a = 1

reinstall
    