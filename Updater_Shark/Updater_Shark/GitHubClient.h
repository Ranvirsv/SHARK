//
//  GitHubClient.h
//  Updater_Shark
//
//  Created by Ranvir Singh Virk on 7/17/23.
//

#ifndef GitHubClient_h
#define GitHubClient_h

#import <Foundation/Foundation.h>
#import "GitHubRelease.h"

@interface GitHubClient : NSObject

- (void)getLatestReleaseForRepo: (void (^_Nullable)(GitHubRelease * _Nullable release, NSError * _Nullable error))completionHandler;

@end


#endif /* GitHubClient_h */
