//
//  GitHubClient.m
//  Updater_Shark
//
//  Created by Ranvir Singh Virk on 7/17/23.
//

#import <Foundation/Foundation.h>
#import "GitHubClient.h"

@implementation GitHubClient

- (void)getLatestReleaseForRepo: (void (^_Nullable)(GitHubRelease * _Nullable release, NSError * _Nullable error))completionHandler {
    NSString *urlString = [NSString stringWithFormat:@"https://api.github.com/repos/nod-ai/SHARK/releases/latest"];
    NSURL *url = [NSURL URLWithString:urlString];
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
    [request setValue:@"application/vnd.github.v3+json" forHTTPHeaderField:@"Accept"];
    
    NSURLSessionDataTask *task = [[NSURLSession sharedSession] dataTaskWithRequest:request completionHandler:^(NSData * _Nullable data, NSURLResponse * _Nullable response, NSError * _Nullable error) {
        if (error){
            NSLog(@"Error in GetLatestRelease: %@", error);
            return;
        }
        
        NSError *jsonError;
        NSDictionary *json = [NSJSONSerialization JSONObjectWithData:data options:0 error:&jsonError];
        
        if (jsonError){
            NSLog(@"JSON Error: %@", jsonError);
            completionHandler(nil, jsonError);
            return;
        }
        
        GitHubRelease *release = [[GitHubRelease alloc] init];
        release.name = json[@"name"];
        release.tagName = json[@"tag_name"];
        release.body = json[@"body"];
        
        NSArray *assets = json[@"assets"];
        if (assets.count > 0){
            NSDictionary *asset = assets.firstObject;
            release.downloadURL = asset[@"browser_download_url"];
        }
        
        completionHandler(release, nil);
    }];
    [task resume];
}

@end
